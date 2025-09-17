from flask import Flask, render_template,redirect,session,request,url_for,flash
from extensions import db
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from itsdangerous import URLSafeSerializer
from flask_mail import Mail,Message
app = Flask(__name__)
app.secret_key = "my_secret_key"

#configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///genecomm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

                flash("Account created successfully! Please log in.", "success")
        else:
            flash("Passwords don't match!", "danger")
            return redirect(url_for("register"))          

    return render_template("register.html")

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
    pass

#route to dashboard
@app.route("/dashboard")
def dashboard():
    if "email" in session:
        return render_template("dashboard.html",email = session["email"])
    return redirect(url_for("home"))

#route for logout button
@app.route("/logout")
def logout():
    session.pop("email")
    return redirect(url_for("index"))

 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)