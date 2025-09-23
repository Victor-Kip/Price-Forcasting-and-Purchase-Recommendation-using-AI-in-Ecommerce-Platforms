from flask import url_for
from flask_mail import Message
from extensions import mail
from utils.token import generate_verification_token

def send_verification_email(user_email):
    token = generate_verification_token(user_email)
    link = url_for("auth.verify_email", token=token, _external=True)
    msg = Message("Verify Your Email", recipients=[user_email])
    msg.body = f"Click the link to verify your account: {link}"
    mail.send(msg)
