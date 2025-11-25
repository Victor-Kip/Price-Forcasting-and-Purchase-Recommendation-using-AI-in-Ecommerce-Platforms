from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
mail = Mail()
oauth = OAuth()
login_manager = LoginManager()
migrate = Migrate()
