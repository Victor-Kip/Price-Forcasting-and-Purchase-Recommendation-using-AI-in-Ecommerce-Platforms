from flask import url_for
from flask_mail import Message
from extensions import mail
from utils.token import generate_verification_token

#account confirmation email after registration
def send_verification_email(user_email):
    token = generate_verification_token(user_email)
    link = url_for("auth.verify_email", token=token, action = "register", _external=True)
    msg = Message("Verify Your Email", recipients=[user_email])
    msg.body = f"Click the link to verify your account: {link}"
    mail.send(msg)

#account confirmation email before reseting password
def send_reset_email(user_mail):
    token  = generate_verification_token(user_mail)
    link = url_for("auth.verify_email",token = token, action = "reset", _external = True)
    msg = Message(" Password reset",recipients=[user_mail])
    msg.body = f"If you requested a password reset,follow this link: {link}"
    mail.send(msg)