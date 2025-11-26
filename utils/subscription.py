
from datetime import date
from extensions import db

def check_forecast_limit(user):
    """
    Checks if the user has reached their daily forecast limit.
    Returns True if allowed, False if limit reached.
    Also handles resetting the count if the day has changed.
    """
    today = date.today()
    
    # Reset count if it's a new day
    if user.last_forecast_date != today:
        user.forecast_count = 0
        user.last_forecast_date = today
        db.session.commit()
    
    # Define limits
    limits = {
        'free': 5,
        'pro': 10,
        'premium': float('inf')
    }
    
    user_tier = user.subscription_tier or 'free'
    limit = limits.get(user_tier, 5)
    
    if user.forecast_count is None:
        user.forecast_count = 0
        db.session.commit()

    if user.forecast_count < limit:
        return True
    else:
        return False

def increment_forecast_count(user):
    """
    Increments the user's forecast count.
    """
    if user.forecast_count is None:
        user.forecast_count = 0
    user.forecast_count += 1
    db.session.commit()
