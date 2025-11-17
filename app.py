from flask import Flask
from config import Config
from extensions import db, mail, oauth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    # register blueprints 
    from routes.auth import auth_bp
    from routes.reset import reset_bp
    from routes.oauth import oauth_bp
    from routes.main import main_bp
    from routes.predict import predict_bp
    from routes.watchlist import watchlist_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reset_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(watchlist_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
