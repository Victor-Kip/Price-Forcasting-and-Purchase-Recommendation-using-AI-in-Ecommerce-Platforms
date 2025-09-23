from api_key import *
class Config:
    SECRET_KEY = "my_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///genecomm.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #configure gmail smtp
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT= 587
    MAIL_USE_TLS = True
    MAIL_USERNAME= SENDER_EMAIL
    MAIL_PASSWORD = MAIL_PASSWORD
    MAIL_DEFAULT_SENDER = SENDER_EMAIL
