
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from flask_login import login_required, current_user
import stripe
import os
from extensions import db
from my_db_models import User

subscription_bp = Blueprint('subscription', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@subscription_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@subscription_bp.route('/create-checkout-session/<tier>', methods=['POST'])
@login_required
def create_checkout_session(tier):
    price_id = None
    if tier == 'pro':
        price_id = os.getenv('STRIPE_PRICE_ID_PRO')
    elif tier == 'premium':
        price_id = os.getenv('STRIPE_PRICE_ID_PREMIUM')
    
    if not price_id:
        flash("Invalid subscription tier selected.", "danger")
        return redirect(url_for('subscription.pricing'))

    # Ensure API key is set
    if not stripe.api_key:
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=current_user.UserID,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('main.dashboard', _external=True) + '?upgrade=success',
            cancel_url=url_for('subscription.pricing', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Error creating checkout session: {str(e)}", "danger")
        return redirect(url_for('subscription.pricing'))

@subscription_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return jsonify(success=True)

def handle_checkout_session(session):
    user_id = session.get('client_reference_id')
    stripe_customer_id = session.get('customer')
    stripe_subscription_id = session.get('subscription')
    
    if user_id:
        user = User.query.get(user_id)
        if user:
            # Determine tier based on price ID (simplified logic)
            # Ideally, you'd fetch the subscription details to confirm the plan
            # For now, we'll assume the webhook logic needs to be robust
            # But we can't easily know the tier from just the session without querying Stripe
            # Let's query the subscription to get the price ID
            try:
                sub = stripe.Subscription.retrieve(stripe_subscription_id)
                price_id = sub['items']['data'][0]['price']['id']
                
                if price_id == os.getenv('STRIPE_PRICE_ID_PRO'):
                    user.subscription_tier = 'pro'
                elif price_id == os.getenv('STRIPE_PRICE_ID_PREMIUM'):
                    user.subscription_tier = 'premium'
                
                user.stripe_customer_id = stripe_customer_id
                user.stripe_subscription_id = stripe_subscription_id
                db.session.commit()
            except Exception as e:
                print(f"Error updating user subscription: {e}")

def handle_subscription_deleted(subscription):
    stripe_customer_id = subscription.get('customer')
    if stripe_customer_id:
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
        if user:
            user.subscription_tier = 'free'
            user.stripe_subscription_id = None
            db.session.commit()
