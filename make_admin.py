from app import create_app
from extensions import db
from my_db_models import User

app = create_app()

def make_admin(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"User {email} is now an admin.")
        else:
            print(f"User {email} not found.")

if __name__ == "__main__":
    email = input("Enter the email of the user to make admin: ")
    make_admin(email)
