from flask import Flask, render_template,redirect,session,request,url_for,flash
from extensions import db
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from itsdangerous import URLSafeSerializer
from flask_mail import Mail,Message
from api_key import *
app = Flask(__name__)
app.secret_key = "my_secret_key"

#configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///genecomm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#configure oauth
oauth = OAuth(app)
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
#configure gmail smtp
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = SENDER_EMAIL
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = SENDER_EMAIL

# initialize mail
mail = Mail(app)

#initialize db with app
db.init_app(app)
from my_db_models import User, Product, PriceHistory, Forecast, Recommendation

#define serializer
serializer = URLSafeSerializer(app.secret_key)
#generate token
def generate_verification_token(email):
    return serializer.dumps(email,salt="email-confirm")
def confirm_token(token,expiration = 3600):
    return serializer.loads(token,salt = "email-confirm",max_age =expiration)
#send verification email
def send_verification_email(user_email):
    token = generate_verification_token(user_email)
    link = url_for('verify_email', token=token, _external=True)
    msg = Message("Verify Your Email", recipients=[user_email])
    msg.body = f"Click to verify your account: {link}"
    mail.send(msg)
#ROUTES
#landing page
@app.route('/')
def index():
    return render_template("index.html")

#route to registration page and process registration details
@app.route('/register', methods = ["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if len(password) < 8:
            flash("Password is too short", "danger")
            return redirect(url_for("register"))
        if(password == confirm_password):
            user = User.query.filter_by(email = email).first()
            if user:
                flash("User already exists!", "warning")
                return redirect(url_for("register"))           
            else:
                new_user = User(email = email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                send_verification_email(email)
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login")) 
        else:
            flash("Passwords don't match!", "danger")
            return redirect(url_for("register"))          
    return render_template("register.html")

#password reset
@app.route("/resetpassword",methods = ["GET","POST"])
def reset_password_request():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email = email).first()
        if user:
            send_verification_email(user)
            flash("If your email exists in our system, you’ll get a reset link.", "info")
        return redirect(url_for("login"))
    return render_template("resetpassword.html")

# route to login page and process login request
@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email = email).first()
        if user and  user.check_password(password):
            session["email"] = email
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials given, try again","error")
            return redirect(url_for("login"))
    return render_template("login.html")
        
#login with google
@app.route("/login/google")
def google_login():
    try:
        redirect_url = url_for("authorize_google",_external = True)
        return google.authorize_redirect(redirect_url)
    except Exception as e:
        app.logger.error(f"An error occurred during login:{str(e)}")
        return "Error during login",500
#email verification
@app.route("/verify/<token>")
def verify_email(token):
    try:
        email = confirm_token(token)
    except Exception:
        return "invalid or expired token"
    user = User.query.filter_by(email = email).first()
    if user:
        session["username"] = email
        return redirect(url_for("dashboard"))
    return "Invalid or expired token"

#google authorization
@app.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata["userinfo_endpoint"]
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()
    email = user_info["email"]

    user = User.query.filter_by(email = email).first()
    if not user:
        user = User(email = email)
        db.session.add(user)
        db.session.commit()
    session["email"] = email
    session["oauth_token"] = token
    return redirect(url_for("dashboard"))

#route to dashboard
@app.route("/dashboard")
def dashboard():
    if "email" in session:
        return render_template("dashboard.html",email = session["email"])
    return redirect(url_for("index"))

#route for logout button
@app.route("/logout")
def logout():
    session.pop("email")
    return redirect(url_for("index"))

 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)