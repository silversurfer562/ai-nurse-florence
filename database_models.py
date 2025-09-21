# Database Models & API Endpoints

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    stripe_customer_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    usage_records = relationship("UsageRecord", back_populates="user")

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True)
    stripe_price_id = Column(String(255))
    tier = Column(String(50), default='free')  # free, basic, pro, enterprise
    status = Column(String(50))  # active, canceled, past_due, etc.
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscription")

class UsageRecord(Base):
    __tablename__ = 'usage_records'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    record_date = Column(DateTime, default=datetime.utcnow)
    api_calls = Column(Integer, default=0)
    storage_used_gb = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="usage_records")

class PaymentEvent(Base):
    __tablename__ = 'payment_events'
    
    id = Column(String(36), primary_key=True)
    stripe_event_id = Column(String(255), unique=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    event_type = Column(String(100))
    event_data = Column(Text)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Service Classes
import uuid
from sqlalchemy.orm import Session

class UserService:
    @staticmethod
    def create_user(db: Session, email: str, name: str = None) -> User:
        """Create a new user and Stripe customer"""
        # Create Stripe customer
        stripe_customer_id = StripeService.create_customer(email, name)
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            stripe_customer_id=stripe_customer_id
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create free subscription record
        subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=user.id,
            tier='free',
            status='active'
        )
        db.add(subscription)
        db.commit()
        
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_subscription(db: Session, user_id: str, subscription_data: dict):
        """Update user's subscription from Stripe webhook"""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if subscription:
            for key, value in subscription_data.items():
                setattr(subscription, key, value)
            subscription.updated_at = datetime.utcnow()
            db.commit()

class UsageService:
    @staticmethod
    def get_monthly_usage(db: Session, user_id: str) -> dict:
        """Get current month's usage for user"""
        from sqlalchemy import func, extract
        
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        
        usage = db.query(
            func.sum(UsageRecord.api_calls).label('total_api_calls'),
            func.max(UsageRecord.storage_used_gb).label('max_storage')
        ).filter(
            UsageRecord.user_id == user_id,
            extract('month', UsageRecord.record_date) == current_month,
            extract('year', UsageRecord.record_date) == current_year
        ).first()
        
        return {
            'api_calls': usage.total_api_calls or 0,
            'storage_gb': usage.max_storage or 0.0
        }
    
    @staticmethod
    def increment_api_calls(db: Session, user_id: str, count: int = 1):
        """Increment API call count for today"""
        today = datetime.utcnow().date()
        
        usage_record = db.query(UsageRecord).filter(
            UsageRecord.user_id == user_id,
            func.date(UsageRecord.record_date) == today
        ).first()
        
        if usage_record:
            usage_record.api_calls += count
        else:
            usage_record = UsageRecord(
                id=str(uuid.uuid4()),
                user_id=user_id,
                api_calls=count
            )
            db.add(usage_record)
        
        db.commit()

# Flask API Endpoints
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_url'
db = SQLAlchemy(app)

@app.route('/api/subscription/create', methods=['POST'])
def create_subscription():
    """Create a new subscription"""
    data = request.json
    user_email = data.get('email')
    price_id = data.get('price_id')
    trial_days = data.get('trial_days', 7)
    
    try:
        # Get or create user
        user = UserService.get_user_by_email(db.session, user_email)
        if not user:
            user = UserService.create_user(
                db.session, 
                user_email, 
                data.get('name')
            )
        
        # Create Stripe subscription
        subscription_data = StripeService.create_subscription(
            user.stripe_customer_id,
            price_id,
            trial_days
        )
        
        # Update local subscription record
        UserService.update_subscription(
            db.session,
            user.id,
            {
                'stripe_subscription_id': subscription_data['id'],
                'stripe_price_id': price_id,
                'status': subscription_data['status'],
                'current_period_end': datetime.fromtimestamp(
                    subscription_data['current_period_end']
                )
            }
        )
        
        return jsonify({
            'success': True,
            'subscription_id': subscription_data['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/subscription/cancel', methods=['POST'])
def cancel_subscription():
    """Cancel a subscription"""
    data = request.json
    subscription_id = data.get('subscription_id')
    at_period_end = data.get('at_period_end', True)
    
    try:
        success = StripeService.cancel_subscription(subscription_id, at_period_end)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to cancel subscription'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/user/entitlements/<user_id>')
def get_user_entitlements(user_id):
    """Get user's current entitlements and usage"""
    try:
        tier = EntitlementService.get_user_tier(user_id)
        limits = EntitlementService.get_usage_limits(user_id)
        usage = UsageService.get_monthly_usage(db.session, user_id)
        
        can_api, remaining_api = EntitlementService.check_api_limit(user_id)
        
        return jsonify({
            'tier': tier.value,
            'limits': {
                'api_calls_per_month': limits.api_calls_per_month,
                'storage_gb': limits.storage_gb,
                'team_members': limits.team_members,
                'advanced_features': limits.advanced_features
            },
            'usage': usage,
            'remaining': {
                'api_calls': remaining_api if remaining_api != -1 else 'unlimited'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    signature = request.headers.get('Stripe-Signature')
    
    if not WebhookHandler.verify_webhook_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 400
    
    try:
        event = json.loads(payload.decode('utf-8'))
        
        # Store event for processing
        payment_event = PaymentEvent(
            id=str(uuid.uuid4()),
            stripe_event_id=event['id'],
            event_type=event['type'],
            event_data=json.dumps(event['data'])
        )
        db.session.add(payment_event)
        db.session.commit()
        
        # Process event
        success = WebhookHandler.handle_webhook_event(
            event['type'], 
            event['data']
        )
        
        if success:
            payment_event.processed = True
            db.session.commit()
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'error': 'Processing failed'}), 500
            
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/check-feature/<feature>')
def check_feature_access(feature):
    """Check if user has access to a feature"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        has_access = EntitlementService.check_feature_access(user_id, feature)
        return jsonify({'has_access': has_access})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Middleware for API rate limiting
from functools import wraps

def check_rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.args.get('user_id') or request.json.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        can_call, remaining = EntitlementService.check_api_limit(user_id)
        
        if not can_call:
            return jsonify({
                'error': 'API limit exceeded',
                'upgrade_url': '/upgrade'
            }), 429
        
        # Track usage
        UsageService.increment_api_calls(db.session, user_id)
        
        return f(*args, **kwargs)
    return decorated_function

# Example protected endpoint
@app.route('/api/premium-feature', methods=['POST'])
@check_rate_limit
def premium_feature():
    """Example premium feature with rate limiting"""
    user_id = request.json.get('user_id')
    
    # Check if user has access to advanced features
    if not EntitlementService.check_feature_access(user_id, 'analytics'):
        return jsonify({
            'error': 'Premium subscription required',
            'upgrade_url': '/upgrade'
        }), 403
    
    # Your premium feature logic here
    return jsonify({'result': 'premium_data'})

if __name__ == '__main__':
    app.run(debug=True)