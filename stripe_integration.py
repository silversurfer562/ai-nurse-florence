# Stripe Integration & Entitlements System

import stripe
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Configuration
stripe.api_key = "your_stripe_secret_key"
STRIPE_WEBHOOK_SECRET = "your_webhook_secret"

class SubscriptionTier(Enum):
    FREE = "free"
    BASIC = "basic" 
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class SubscriptionLimits:
    api_calls_per_month: int
    storage_gb: int
    team_members: int
    advanced_features: bool

# Subscription tier configurations
TIER_LIMITS = {
    SubscriptionTier.FREE: SubscriptionLimits(100, 1, 1, False),
    SubscriptionTier.BASIC: SubscriptionLimits(1000, 10, 3, False),
    SubscriptionTier.PRO: SubscriptionLimits(10000, 100, 10, True),
    SubscriptionTier.ENTERPRISE: SubscriptionLimits(-1, -1, -1, True)  # -1 = unlimited
}

class StripeService:
    """Handle all Stripe operations"""
    
    @staticmethod
    def create_customer(email: str, name: str = None) -> str:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={'created_from': 'app_signup'}
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create customer: {str(e)}")
    
    @staticmethod
    def create_subscription(customer_id: str, price_id: str, trial_days: int = 7) -> Dict[str, Any]:
        """Create a new subscription with optional trial"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                trial_period_days=trial_days if trial_days > 0 else None,
                metadata={'source': 'web_app'}
            )
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end,
                'trial_end': subscription.trial_end
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'items': [item.price.id for item in subscription.items.data]
            }
        except stripe.error.StripeError:
            return None
    
    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> bool:
        """Cancel a subscription"""
        try:
            if at_period_end:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.StripeError:
            return False

class WebhookHandler:
    """Handle Stripe webhook events"""
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """Verify webhook signature for security"""
        try:
            stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
            return True
        except ValueError:
            # Invalid payload
            return False
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return False
    
    @staticmethod
    def handle_webhook_event(event_type: str, event_data: Dict[str, Any]) -> bool:
        """Route webhook events to appropriate handlers"""
        handlers = {
            'customer.subscription.created': WebhookHandler._handle_subscription_created,
            'customer.subscription.updated': WebhookHandler._handle_subscription_updated,
            'customer.subscription.deleted': WebhookHandler._handle_subscription_deleted,
            'invoice.payment_succeeded': WebhookHandler._handle_payment_succeeded,
            'invoice.payment_failed': WebhookHandler._handle_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event_data)
        return True  # Unknown event, but don't fail
    
    @staticmethod
    def _handle_subscription_created(data: Dict[str, Any]) -> bool:
        """Handle new subscription creation"""
        subscription = data['object']
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        status = subscription['status']
        
        # Update user subscription status in your database
        # UserService.update_subscription(customer_id, subscription_id, status)
        print(f"Subscription created: {subscription_id} for customer {customer_id}")
        return True
    
    @staticmethod
    def _handle_subscription_updated(data: Dict[str, Any]) -> bool:
        """Handle subscription changes"""
        subscription = data['object']
        subscription_id = subscription['id']
        status = subscription['status']
        
        # Update subscription status
        # UserService.update_subscription_status(subscription_id, status)
        print(f"Subscription updated: {subscription_id} - Status: {status}")
        return True
    
    @staticmethod
    def _handle_subscription_deleted(data: Dict[str, Any]) -> bool:
        """Handle subscription cancellation"""
        subscription = data['object']
        subscription_id = subscription['id']
        
        # Downgrade user to free tier
        # UserService.downgrade_to_free(subscription_id)
        print(f"Subscription cancelled: {subscription_id}")
        return True
    
    @staticmethod
    def _handle_payment_succeeded(data: Dict[str, Any]) -> bool:
        """Handle successful payment"""
        invoice = data['object']
        customer_id = invoice['customer']
        
        # Send payment confirmation email
        # EmailService.send_payment_confirmation(customer_id)
        print(f"Payment succeeded for customer: {customer_id}")
        return True
    
    @staticmethod
    def _handle_payment_failed(data: Dict[str, Any]) -> bool:
        """Handle failed payment"""
        invoice = data['object']
        customer_id = invoice['customer']
        
        # Send payment failure notification
        # EmailService.send_payment_failure_notice(customer_id)
        print(f"Payment failed for customer: {customer_id}")
        return True

class EntitlementService:
    """Handle user entitlements and feature access"""
    
    @staticmethod
    def get_user_tier(user_id: str) -> SubscriptionTier:
        """Get user's current subscription tier"""
        # This would query your database
        # For now, return a default
        # user = UserService.get_user(user_id)
        # return SubscriptionTier(user.subscription_tier)
        return SubscriptionTier.FREE
    
    @staticmethod
    def get_usage_limits(user_id: str) -> SubscriptionLimits:
        """Get user's usage limits based on their tier"""
        tier = EntitlementService.get_user_tier(user_id)
        return TIER_LIMITS[tier]
    
    @staticmethod
    def check_api_limit(user_id: str) -> tuple[bool, int]:
        """Check if user can make API calls"""
        limits = EntitlementService.get_usage_limits(user_id)
        # current_usage = UsageService.get_monthly_api_calls(user_id)
        current_usage = 0  # Placeholder
        
        if limits.api_calls_per_month == -1:  # Unlimited
            return True, -1
        
        remaining = limits.api_calls_per_month - current_usage
        return remaining > 0, remaining
    
    @staticmethod
    def check_storage_limit(user_id: str, additional_gb: float) -> bool:
        """Check if user can use additional storage"""
        limits = EntitlementService.get_usage_limits(user_id)
        # current_usage = UsageService.get_storage_usage_gb(user_id)
        current_usage = 0  # Placeholder
        
        if limits.storage_gb == -1:  # Unlimited
            return True
        
        return (current_usage + additional_gb) <= limits.storage_gb
    
    @staticmethod
    def check_feature_access(user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        limits = EntitlementService.get_usage_limits(user_id)
        
        # Feature-specific checks
        advanced_features = ['analytics', 'api_access', 'custom_integrations']
        if feature in advanced_features:
            return limits.advanced_features
        
        return True  # Basic features available to all

# Usage tracking decorator
def track_api_usage(func):
    """Decorator to track API usage"""
    def wrapper(user_id: str, *args, **kwargs):
        # Check if user can make API calls
        can_call, remaining = EntitlementService.check_api_limit(user_id)
        
        if not can_call:
            raise Exception("API limit exceeded. Please upgrade your plan.")
        
        # Track the API call
        # UsageService.increment_api_calls(user_id)
        
        return func(user_id, *args, **kwargs)
    return wrapper

# Example usage middleware/decorator
def require_subscription(tier: SubscriptionTier):
    """Decorator to require minimum subscription tier"""
    def decorator(func):
        def wrapper(user_id: str, *args, **kwargs):
            user_tier = EntitlementService.get_user_tier(user_id)
            tier_levels = {
                SubscriptionTier.FREE: 0,
                SubscriptionTier.BASIC: 1,
                SubscriptionTier.PRO: 2,
                SubscriptionTier.ENTERPRISE: 3
            }
            
            if tier_levels[user_tier] < tier_levels[tier]:
                raise Exception(f"This feature requires {tier.value} subscription")
            
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator

# Example API endpoints (Flask/FastAPI style)
@track_api_usage
@require_subscription(SubscriptionTier.BASIC)
def premium_api_endpoint(user_id: str, data: Dict[str, Any]):
    """Example premium API endpoint with usage tracking"""
    # Your API logic here
    return {"status": "success", "data": "premium_feature_result"}

# Webhook endpoint example
def stripe_webhook_endpoint(request_body: bytes, signature: str):
    """Handle incoming Stripe webhooks"""
    if not WebhookHandler.verify_webhook_signature(request_body, signature):
        return {"error": "Invalid signature"}, 400
    
    try:
        event = json.loads(request_body.decode('utf-8'))
        event_type = event['type']
        event_data = event['data']
        
        success = WebhookHandler.handle_webhook_event(event_type, event_data)
        
        if success:
            return {"status": "success"}, 200
        else:
            return {"error": "Failed to process event"}, 500
            
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}, 400
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return {"error": "Internal error"}, 500