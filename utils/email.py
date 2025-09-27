from flask import url_for
from flask_mail import Message
from extensions import mail,db
from utils.token import generate_verification_token
from utils.otps import generate_otp
from my_db_models import User
#account confirmation email after registration
def send_verification_email(user_email):
    otp = generate_otp()
    user = User.query.filter_by(email=user_email).first()
    user.otp = otp
    db.session.commit()
    token = generate_verification_token(user_email)
    link = url_for("auth.verify_email", token=token, action = "register", _external=True)
    msg = Message("Verify Your Email", recipients=[user_email])
    msg.body = f"Your OTP is: {otp} ,or Click the link to verify your account: {link}"
    mail.send(msg)

#account confirmation email before reseting password
def send_reset_email(user_mail):
    otp = generate_otp()
    user = User.query.filter_by(email=user_mail).first()
    user.otp = otp
    db.session.commit()
    token  = generate_verification_token(user_mail)
    link = url_for("auth.verify_email",token = token, action = "reset", _external = True)
    msg = Message(" Password reset",recipients=[user_mail])
    msg.body = f"If you requested a password reset, use the OTP : {otp},or follow this link: {link}"
    mail.send(msg)