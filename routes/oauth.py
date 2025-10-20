from flask import Blueprint, session, redirect, url_for,current_app
from extensions import oauth
from extensions import db
from my_db_models import User
oauth_bp = Blueprint("oauth", __name__)

from api_key import *
#configure oauth
google = oauth.register(
    name="google",
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"}
)

#login with google
@oauth_bp.route("/login/google")
def google_login():
    try:
        redirect_url = url_for("oauth.authorize_google",_external = True)
        return google.authorize_redirect(redirect_url)
    except Exception as e:
        current_app.logger.error(f"An error occurred during login: {str(e)}")
    return "Error during login", 500

#google authorization
@oauth_bp.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata["userinfo_endpoint"]
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()

    email = user_info["email"]
    name = user_info.get("name",email.split("@")[0])
    picture = user_info.get("picture")

    user = User.query.filter_by(email = email).first()
    #register new user
    if not user:
        user = User(email = email,username = name,profile_image = picture)
        db.session.add(user)
        db.session.commit()
    else:
        if not user.username:
            user.username = name
        if not user.profile_image and picture:
            user.profile_image = picture
        db.session.commit()
    #store in session for dashboard
    session["email"] = email
    session["username"] = user.username
    session["profile_image"] = user.profile_image
    return redirect(url_for("main.dashboard"))