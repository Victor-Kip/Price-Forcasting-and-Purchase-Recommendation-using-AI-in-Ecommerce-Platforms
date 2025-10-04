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
                flash("Account created successfully! Please check your email to verify your account.", "success")
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
            if not user.is_verified:
                flash("Please verify your email before logging in.", "warning")
                return redirect(url_for("auth.login"))
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
    session.pop("username",None)
    session.pop("profile_image",None)
    return redirect(url_for("main.index"))

# Email verification
@auth_bp.route("/verify/<token>")
def verify_email(token):
    action = request.args.get("action", "register")
    email = confirm_token(token)
    if not email:
        flash("Invalid or expired token", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("No account found for this verification link.", "danger")
        return redirect(url_for("auth.register"))
    if action == "register":
        if user.is_verified:
            flash("Account already verified. Please login.", "info")
            return redirect(url_for("auth.login"))
        user.is_verified = True
        db.session.commit()
        flash("Email verified successfully! You can now log in", "success")
        return redirect(url_for("auth.login"))
    
    elif action == "reset":
        session["email"] = email
        return redirect(url_for("reset.reset_password"))
    flash("Unknown verification action.", "danger")
    return redirect(url_for("auth.login"))

@auth_bp.route("/verify/otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        otp = request.form.get("otp")
        user = User.query.filter_by(email=session.get("verify_email")).first()
        if user:
            if user.otp == otp:
                flash("Email verified successfully!", "success")
                return redirect(url_for("reset.reset_password"))
            flash("Invalid OTP", "danger")
        flash("User doesn't exist","danger")
    return render_template("verify_otp.html")


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    user = User.query.filter_by(email=session.get("email")).first()
    if user:
        send_verification_email(user.email)
        flash("A new OTP has been sent to your email.", "info")
    return redirect(url_for("auth.verify_otp"))

@auth_bp.route("/accountsettings", methods=["GET", "POST"])
def account_settings():
    if "email" not in session:
        flash("Please login to continue", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=session["email"]).first()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")

        # update fields
        user.Name = username
        user.email = email
        db.session.commit()
        flash("Account updated successfully", "success")
        return redirect(url_for("auth.account_settings"))

    # for GET request → just show the page
    return render_template("accountsettings.html", user=user)

