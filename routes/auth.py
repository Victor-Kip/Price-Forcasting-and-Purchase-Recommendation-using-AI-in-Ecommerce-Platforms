from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from my_db_models import User
from utils.token import confirm_token
from utils.email import send_verification_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Register
@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if len(password) < 8:
            flash("Password is too short", "danger")
            return redirect(url_for("auth.register"))

        if password == confirm_password:
            user = User.query.filter_by(email=email).first()
            if user:
                flash("User already exists!", "warning")
                return redirect(url_for("auth.register"))
            else:
                new_user = User(email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                send_verification_email(email)
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("auth.login"))
        else:
            flash("Passwords don't match!", "danger")
            return redirect(url_for("auth.register"))

    return render_template("register.html")

# Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["email"] = email
            return redirect(url_for("main.dashboard")) 
        else:
            flash("Invalid credentials given, try again", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

# Logout
@auth_bp.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("main.index"))

# Email verification
@auth_bp.route("/verify/<token>")
def verify_email(token):
    try:
        email = confirm_token(token)
    except Exception:
        flash("Invalid or expired token", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if user:
        session["email"] = email
        flash("Email verified successfully!", "success")
        return redirect(url_for("main.dashboard"))

    flash("Verification failed.", "danger")
    return redirect(url_for("auth.login"))
