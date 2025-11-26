from flask import Flask
from dotenv import load_dotenv
import os

# Load env vars before importing config
load_dotenv()

from config import Config
from extensions import db, mail, oauth, login_manager, migrate
from my_db_models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints 
    from routes.auth import auth_bp
    from routes.reset import reset_bp
    from routes.oauth import oauth_bp
    from routes.main import main_bp
    from routes.predict import predict_bp
    from routes.watchlist import watchlist_bp
    from routes.recommendation import recommendation_bp
    from routes.subscription import subscription_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reset_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(subscription_bp, url_prefix='/subscription')
    # app.register_blueprint(admin_bp) # Commenting out admin_bp if it doesn't exist yet or was removed

    with app.app_context():
        db.create_all()

    return app
    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
