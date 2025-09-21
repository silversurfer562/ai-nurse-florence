# main.py - Production-Ready FastAPI Stripe Integration
# Updated for AI Nurse Florence with security improvements

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SQLEnum, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import stripe
import hmac
import hashlib
import json
import os
import jwt
import secrets
import logging
from passlib.context import CryptContext

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = ENVIRONMENT == 'development'

# Stripe Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable is required")

STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
if not STRIPE_WEBHOOK_SECRET:
    raise ValueError("STRIPE_WEBHOOK_SECRET environment variable is required")

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    if DEBUG:
        DATABASE_URL = 'sqlite:///./ai_nurse_florence.db'
        logger.warning("Using SQLite for development. Use PostgreSQL for production.")
    else:
        raise ValueError("DATABASE_URL environment variable is required for production")

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    if DEBUG:
        JWT_SECRET = secrets.token_urlsafe(32)
        logger.warning(f"Generated JWT secret for development: {JWT_SECRET}")
    else:
        raise ValueError("JWT_SECRET environment variable is required for production")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Setup
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI App
app = FastAPI(
    title="AI Nurse Florence API",
    description="Subscription management and entitlements API",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if DEBUG else None
)

# Security Middleware
if not DEBUG:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )

# CORS Configuration
allowed_origins = [
    "http://localhost:3000",  # Development
    "https://localhost:3000",  # Development HTTPS
]

if not DEBUG:
    # Add your production domains
    allowed_origins.extend([
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        # Add your actual domain here
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Enums
class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # For future password auth
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    subscription_end_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    subscriptions = relationship("Subscription", back_populates="user")
    api_usage = relationship("ApiUsage", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_price_id = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    canceled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="subscriptions")

class ApiUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    usage_date = Column(DateTime, default=datetime.utcnow)
    usage_month = Column(String(7), nullable=False)  # YYYY-MM format
    count = Column(Integer, default=1)
    
    # Relationship
    user = relationship("User", back_populates="api_usage")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    
    @validator('email')
    def validate_email(cls, v):
        if not v or len(v) < 5:
            raise ValueError('Valid email is required')
        return v.lower()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SubscriptionCreate(BaseModel):
    price_id: str
    trial_days: Optional[int] = None
    
    @validator('price_id')
    def validate_price_id(cls, v):
        if not v or not v.startswith('price_'):
            raise ValueError('Valid Stripe price ID is required')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    subscription_tier: SubscriptionTier
    subscription_status: SubscriptionStatus
    subscription_end_date: Optional[datetime]
    trial_end_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class EntitlementsResponse(BaseModel):
    tier: SubscriptionTier
    features: List[str]
    limits: Dict[str, Any]
    support_level: str

class PaymentIntentResponse(BaseModel):
    client_secret: str
    subscription_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# Entitlement Configuration
ENTITLEMENTS = {
    SubscriptionTier.FREE: {
        'api_calls_per_month': 100,
        'storage_gb': 1,
        'max_conversations': 10,
        'features': ['basic_chat', 'export_csv'],
        'support_level': 'community'
    },
    SubscriptionTier.BASIC: {
        'api_calls_per_month': 1000,
        'storage_gb': 10,
        'max_conversations': 100,
        'features': ['basic_chat', 'export_csv', 'advanced_analysis', 'email_support'],
        'support_level': 'email'
    },
    SubscriptionTier.PREMIUM: {
        'api_calls_per_month': 10000,
        'storage_gb': 100,
        'max_conversations': 1000,
        'features': ['basic_chat', 'export_csv', 'advanced_analysis', 'email_support', 'api_access', 'priority_processing'],
        'support_level': 'priority'
    },
    SubscriptionTier.ENTERPRISE: {
        'api_calls_per_month': -1,  # unlimited
        'storage_gb': -1,  # unlimited
        'max_conversations': -1,  # unlimited
        'features': ['all'],
        'support_level': 'dedicated'
    }
}

# Stripe Price IDs - Update with your actual price IDs
STRIPE_PRICE_IDS = {
    SubscriptionTier.BASIC: os.getenv('STRIPE_BASIC_PRICE_ID'),
    SubscriptionTier.PREMIUM: os.getenv('STRIPE_PREMIUM_PRICE_ID'),
    SubscriptionTier.ENTERPRISE: os.getenv('STRIPE_ENTERPRISE_PRICE_ID')
}

# Validate price IDs
for tier, price_id in STRIPE_PRICE_IDS.items():
    if not price_id:
        logger.warning(f"Missing price ID for {tier.value}")

# Dependency Functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    
    return user

# Helper Functions
def verify_stripe_signature(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature for security"""
    try:
        stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
        return True
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"Stripe signature verification failed: {e}")
        return False

def get_user_entitlements(user: User) -> Dict[str, Any]:
    """Get current entitlements for a user"""
    return ENTITLEMENTS.get(user.subscription_tier, ENTITLEMENTS[SubscriptionTier.FREE])

def check_feature_access(user: User, feature: str) -> bool:
    """Check if user has access to a specific feature"""
    entitlements = get_user_entitlements(user)
    features = entitlements['features']
    return feature in features or 'all' in features

def get_monthly_usage(user: User, db: Session) -> int:
    """Get current month's API usage for user"""
    current_month = datetime.utcnow().strftime('%Y-%m')
    usage = db.query(ApiUsage).filter(
        ApiUsage.user_id == user.id,
        ApiUsage.usage_month == current_month
    ).first()
    return usage.count if usage else 0

def check_usage_limit(user: User, db: Session) -> bool:
    """Check if user is within monthly usage limits"""
    entitlements = get_user_entitlements(user)
    limit = entitlements.get('api_calls_per_month', 0)
    if limit == -1:  # unlimited
        return True
    
    current_usage = get_monthly_usage(user, db)
    return current_usage < limit

def increment_usage(user: User, endpoint: str, db: Session):
    """Increment API usage for user"""
    current_month = datetime.utcnow().strftime('%Y-%m')
    usage = db.query(ApiUsage).filter(
        ApiUsage.user_id == user.id,
        ApiUsage.usage_month == current_month,
        ApiUsage.endpoint == endpoint
    ).first()
    
    if usage:
        usage.count += 1
        usage.usage_date = datetime.utcnow()
    else:
        usage = ApiUsage(
            user_id=user.id,
            endpoint=endpoint,
            usage_month=current_month,
            count=1
        )
        db.add(usage)
    
    db.commit()

def create_stripe_customer(email: str) -> str:
    """Create a new Stripe customer"""
    try:
        customer = stripe.Customer.create(email=email)
        return customer.id
    except stripe.error.StripeError as e:
        logger.error(f"Failed to create Stripe customer: {e}")
        raise HTTPException(status_code=400, detail="Failed to create customer")

def get_tier_from_price_id(price_id: str) -> SubscriptionTier:
    """Get subscription tier from Stripe price ID"""
    for tier, tier_price_id in STRIPE_PRICE_IDS.items():
        if tier_price_id == price_id:
            return tier
    return SubscriptionTier.FREE

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "AI Nurse Florence API", 
        "status": "running",
        "environment": ENVIRONMENT,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create Stripe customer
    stripe_customer_id = create_stripe_customer(user_data.email)
    
    # Create user in database
    db_user = User(
        email=user_data.email,
        stripe_customer_id=stripe_customer_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.id})
    
    logger.info(f"New user registered: {user_data.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600
    )

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/api/users/me/entitlements", response_model=EntitlementsResponse)
async def get_user_entitlements_endpoint(current_user: User = Depends(get_current_user)):
    """Get user's current entitlements"""
    entitlements = get_user_entitlements(current_user)
    return EntitlementsResponse(
        tier=current_user.subscription_tier,
        features=entitlements['features'],
        limits={k: v for k, v in entitlements.items() if k not in ['features', 'support_level']},
        support_level=entitlements['support_level']
    )

@app.get("/api/users/me/usage")
async def get_user_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current usage statistics"""
    current_usage = get_monthly_usage(current_user, db)
    entitlements = get_user_entitlements(current_user)
    limit = entitlements.get('api_calls_per_month', 0)
    
    return {
        "current_usage": current_usage,
        "limit": limit,
        "within_limit": check_usage_limit(current_user, db),
        "percentage_used": (current_usage / limit * 100) if limit > 0 else 0,
        "tier": current_user.subscription_tier
    }

@app.post("/api/subscriptions/create-payment-intent", response_model=PaymentIntentResponse)
async def create_subscription_payment_intent(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment intent for subscription"""
    try:
        # Validate price ID
        if subscription_data.price_id not in STRIPE_PRICE_IDS.values():
            raise HTTPException(status_code=400, detail="Invalid price ID")
        
        # Create subscription
        subscription_params = {
            'customer': current_user.stripe_customer_id,
            'items': [{'price': subscription_data.price_id}],
            'payment_behavior': 'default_incomplete',
            'payment_settings': {'save_default_payment_method': 'on_subscription'},
            'expand': ['latest_invoice.payment_intent'],
        }
        
        if subscription_data.trial_days:
            subscription_params['trial_period_days'] = subscription_data.trial_days
        
        stripe_subscription = stripe.Subscription.create(**subscription_params)
        
        # Save subscription to database
        tier = get_tier_from_price_id(subscription_data.price_id)
        db_subscription = Subscription(
            user_id=current_user.id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_price_id=subscription_data.price_id,
            status=stripe_subscription.status,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end)
        )
        db.add(db_subscription)
        
        # Update user subscription info
        current_user.subscription_tier = tier
        current_user.subscription_status = SubscriptionStatus(stripe_subscription.status)
        if subscription_data.trial_days:
            current_user.trial_end_date = datetime.utcnow() + timedelta(days=subscription_data.trial_days)
        
        db.commit()
        
        logger.info(f"Created subscription for user {current_user.email}: {tier.value}")
        
        return PaymentIntentResponse(
            client_secret=stripe_subscription.latest_invoice.payment_intent.client_secret,
            subscription_id=stripe_subscription.id
        )
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Stripe webhooks"""
    payload = await request.body()
    signature = request.headers.get('stripe-signature')
    
    if not verify_stripe_signature(payload, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    # Handle different webhook events
    event_handlers = {
        'customer.subscription.created': handle_subscription_created,
        'customer.subscription.updated': handle_subscription_updated,
        'customer.subscription.deleted': handle_subscription_deleted,
        'invoice.payment_succeeded': handle_payment_succeeded,
        'invoice.payment_failed': handle_payment_failed,
    }
    
    handler = event_handlers.get(event.type)
    if handler:
        background_tasks.add_task(handler, event.data.object)
    
    logger.info(f"Processed webhook event: {event.type}")
    return {"status": "success"}

# Background Tasks for Webhook Processing
async def handle_subscription_created(subscription):
    """Handle subscription created event"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.stripe_customer_id == subscription.customer).first()
        if not user:
            return
        
        price_id = subscription.items.data[0].price.id
        tier = get_tier_from_price_id(price_id)
        
        user.subscription_tier = tier
        user.subscription_status = SubscriptionStatus(subscription.status)
        user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
        
        db.commit()
        logger.info(f"Subscription created for user {user.email}: {tier.value}")
    finally:
        db.close()

async def handle_subscription_updated(subscription):
    """Handle subscription updated event"""
    db = SessionLocal()
    try:
        db_subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription.id
        ).first()
        
        if db_subscription:
            db_subscription.status = subscription.status
            db_subscription.current_period_start = datetime.fromtimestamp(subscription.current_period_start)
            db_subscription.current_period_end = datetime.fromtimestamp(subscription.current_period_end)
            
            user = db.query(User).filter(User.id == db_subscription.user_id).first()
            if user:
                user.subscription_status = SubscriptionStatus(subscription.status)
                user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
            
            db.commit()
            logger.info(f"Subscription updated: {subscription.id}")
    finally:
        db.close()

async def handle_subscription_deleted(subscription):
    """Handle subscription deleted event"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.stripe_customer_id == subscription.customer).first()
        if user:
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_status = SubscriptionStatus.CANCELED
            db.commit()
            logger.info(f"Subscription canceled for user {user.email}")
    finally:
        db.close()

async def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    logger.info(f"Payment succeeded for invoice: {invoice.id}")

async def handle_payment_failed(invoice):
    """Handle failed payment"""
    logger.error(f"Payment failed for invoice: {invoice.id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info" if DEBUG else "warning"
    )