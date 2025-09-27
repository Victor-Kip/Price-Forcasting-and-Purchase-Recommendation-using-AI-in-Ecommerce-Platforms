from itsdangerous import URLSafeSerializer
from flask import current_app

def generate_verification_token(email):
    serializer = URLSafeSerializer(current_app.secret_key)
    return serializer.dumps(email, salt="email-confirm")

def confirm_token(token, expiration=3600):
    serializer = URLSafeSerializer(current_app.secret_key)
    return serializer.loads(token, salt="email-confirm", max_age=expiration)
