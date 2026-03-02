import stripe
from django.conf import settings
from django.http import HttpResponse
from .models import User

# Initialize Stripe with the secret key from .env
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    """
    Handles monetization logic for the Integrated Medicine community.
    Manages the link between Django Users and Stripe Customers.
    """

    @staticmethod
    def create_or_get_customer(user_id):
        """
        Ensures every Django user has a corresponding Stripe Customer ID.
        """
        user = User.objects.get(id=user_id)
        
        if user.stripe_customer_id:
            return user.stripe_customer_id

        # Create new customer in Stripe
        customer = stripe.Customer.create(
            email=user.email,
            metadata={'user_id': user.id}
        )
        
        user.stripe_customer_id = customer.id
        user.save()
        return customer.id

    @staticmethod
    def create_checkout_session(user_id, price_id):
        """
        Generates a secure Stripe Checkout URL for the React frontend.
        """
        customer_id = StripeService.create_or_get_customer(user_id)
        
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=f"{settings.FRONTEND_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
        )
        return session.url

def handle_stripe_webhook(payload, sig_header):
    """
    The 'Source of Truth' for user access. 
    Processes events from Stripe to grant or revoke 'Premium' access.
    """
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400) # Invalid payload
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400) # Invalid signature

    # 1. Handle Successful Payment (Grant Access)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session.get('customer')
        
        user = User.objects.filter(stripe_customer_id=customer_id).first()
        if user:
            user.is_premium = True
            user.save()
            # Logic here: Trigger Circle.so API to invite user to 'Premium Spaces'
            print(f"Access GRANTED for user: {user.email}")

    # 2. Handle Subscription Cancellation (Revoke Access)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        
        user = User.objects.filter(stripe_customer_id=customer_id).first()
        if user:
            user.is_premium = False
            user.save()
            # Logic here: Trigger Circle.so API to remove user from 'Premium Spaces'
            print(f"Access REVOKED for user: {user.email}")

    return HttpResponse(status=200)
