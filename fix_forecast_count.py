from extensions import db
from my_db_models import User

# One-time script to set all NULL forecast_count values to 0
def fix_null_forecast_count():
    users = User.query.filter(User.forecast_count == None).all()
    for user in users:
        user.forecast_count = 0
    db.session.commit()
    print(f"Updated {len(users)} users with NULL forecast_count.")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fix_null_forecast_count()
