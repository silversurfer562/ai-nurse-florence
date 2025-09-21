# main.py - FastAPI Stripe Integration
# Save this file as main.py in your project root

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SQLEnum, Boolean, ForeignKey
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

# Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_key_here')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')  # Using SQLite for easier setup
JWT_SECRET = os.getenv('JWT_SECRET', 'your-jwt-secret-change-this')

# Database Setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI App
app = FastAPI(title="AI Nurse Florence Subscription API", version="1.0.0")

# CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)  # Made optional for easier testing

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

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    stripe_customer_id = Column(String, unique=True, nullable=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    subscription_end_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    subscriptions = relationship("Subscription", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String, unique=True, nullable=False)
    stripe_price_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="subscriptions")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models for API
class UserCreate(BaseModel):
    email: EmailStr

class SubscriptionCreate(BaseModel):
    price_id: str
    trial_days: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: str
    subscription_tier: SubscriptionTier
    subscription_status: SubscriptionStatus
    subscription_end_date: Optional[datetime]
    trial_end_date: Optional[datetime]
    
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

# Entitlement Configuration
ENTITLEMENTS = {
    SubscriptionTier.FREE: {
        'api_calls_per_month': 100,
        'storage_gb': 1,
        'max_projects': 1,
        'features': ['basic_search', 'export_csv'],
        'support_level': 'community'
    },
    SubscriptionTier.BASIC: {
        'api_calls_per_month': 10000,
        'storage_gb': 10,
        'max_projects': 5,
        'features': ['basic_search', 'export_csv', 'advanced_filters', 'email_support'],
        'support_level': 'email'
    },
    SubscriptionTier.PREMIUM: {
        'api_calls_per_month': 100000,
        'storage_gb': 100,
        'max_projects': 25,
        'features': ['basic_search', 'export_csv', 'advanced_filters', 'email_support', 'api_access', 'custom_integrations'],
        'support_level': 'priority'
    },
    SubscriptionTier.ENTERPRISE: {
        'api_calls_per_month': -1,
        'storage_gb': -1,
        'max_projects': -1,
        'features': ['all'],
        'support_level': 'dedicated'
    }
}

# Stripe Price IDs - Update these with your actual Stripe price IDs
STRIPE_PRICE_IDS = {
    SubscriptionTier.BASIC: os.getenv('STRIPE_BASIC_PRICE_ID', 'price_basic_test'),
    SubscriptionTier.PREMIUM: os.getenv('STRIPE_PREMIUM_PRICE_ID', 'price_premium_test'),
    SubscriptionTier.ENTERPRISE: os.getenv('STRIPE_ENTERPRISE_PRICE_ID', 'price_enterprise_test')
}

# Dependency Functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user from JWT token - Optional for testing"""
    if not credentials:
        # For testing purposes, return a dummy user
        user = db.query(User).first()
        if not user:
            # Create a test user
            user = User(email="test@example.com")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Helper Functions
def verify_stripe_signature(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature for security"""
    if not STRIPE_WEBHOOK_SECRET or STRIPE_WEBHOOK_SECRET == 'whsec_your_webhook_secret':
        return True  # Skip verification for testing
    
    try:
        stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
        return True
    except (ValueError, stripe.error.StripeError):
        return False

def get_user_entitlements(user: User) -> Dict[str, Any]:
    """Get current entitlements for a user"""
    return ENTITLEMENTS.get(user.subscription_tier, ENTITLEMENTS[SubscriptionTier.FREE])

def check_feature_access(user: User, feature: str) -> bool:
    """Check if user has access to a specific feature"""
    entitlements = get_user_entitlements(user)
    features = entitlements['features']
    return feature in features or 'all' in features

def check_usage_limit(user: User, resource_type: str, current_usage: int) -> bool:
    """Check if user is within usage limits"""
    entitlements = get_user_entitlements(user)
    limit = entitlements.get(resource_type, 0)
    if limit == -1:  # unlimited
        return True
    return current_usage < limit

def create_stripe_customer(email: str) -> str:
    """Create a new Stripe customer"""
    try:
        customer = stripe.Customer.create(email=email)
        return customer.id
    except stripe.error.StripeError as e:
        # For testing, return a dummy customer ID
        return f"cus_test_{email.replace('@', '_').replace('.', '_')}"

def get_tier_from_price_id(price_id: str) -> SubscriptionTier:
    """Get subscription tier from Stripe price ID"""
    for tier, tier_price_id in STRIPE_PRICE_IDS.items():
        if tier_price_id == price_id:
            return tier
    return SubscriptionTier.FREE

# API Endpoints

@app.get("/")
async def root():
    return {"message": "AI Nurse Florence Subscription API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
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
    
    return db_user

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

@app.get("/api/features/{feature_name}/check")
async def check_feature_access_endpoint(feature_name: str, current_user: User = Depends(get_current_user)):
    """Check if user has access to a specific feature"""
    has_access = check_feature_access(current_user, feature_name)
    return {"feature": feature_name, "has_access": has_access}

@app.get("/api/usage/{resource_type}/check")
async def check_usage_limit_endpoint(
    resource_type: str,
    current_usage: int,
    current_user: User = Depends(get_current_user)
):
    """Check if user is within usage limits"""
    within_limit = check_usage_limit(current_user, resource_type, current_usage)
    entitlements = get_user_entitlements(current_user)
    limit = entitlements.get(resource_type, 0)
    
    return {
        "resource_type": resource_type,
        "current_usage": current_usage,
        "limit": limit,
        "within_limit": within_limit,
        "percentage_used": (current_usage / limit * 100) if limit > 0 else 0
    }

@app.post("/api/subscriptions/create-payment-intent", response_model=PaymentIntentResponse)
async def create_subscription_payment_intent(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment intent for subscription"""
    try:
        # For testing without real Stripe integration
        if stripe.api_key == 'sk_test_your_key_here':
            return PaymentIntentResponse(
                client_secret="pi_test_client_secret",
                subscription_id="sub_test_subscription"
            )
        
        # Real Stripe integration
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
        
        return PaymentIntentResponse(
            client_secret=stripe_subscription.latest_invoice.payment_intent.client_secret,
            subscription_id=stripe_subscription.id
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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
    if event.type == 'customer.subscription.created':
        background_tasks.add_task(handle_subscription_created, event.data.object, db)
    elif event.type == 'customer.subscription.updated':
        background_tasks.add_task(handle_subscription_updated, event.data.object, db)
    elif event.type == 'customer.subscription.deleted':
        background_tasks.add_task(handle_subscription_deleted, event.data.object, db)
    
    return {"status": "success"}

# Background Tasks for Webhook Processing
async def handle_subscription_created(subscription, db: Session):
    """Handle subscription created event"""
    user = db.query(User).filter(User.stripe_customer_id == subscription.customer).first()
    if not user:
        return
    
    price_id = subscription.items.data[0].price.id
    tier = get_tier_from_price_id(price_id)
    
    user.subscription_tier = tier
    user.subscription_status = SubscriptionStatus(subscription.status)
    user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
    
    db.commit()

async def handle_subscription_updated(subscription, db: Session):
    """Handle subscription updated event"""
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

async def handle_subscription_deleted(subscription, db: Session):
    """Handle subscription deleted event"""
    user = db.query(User).filter(User.stripe_customer_id == subscription.customer).first()
    if user:
        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_status = SubscriptionStatus.CANCELED
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)