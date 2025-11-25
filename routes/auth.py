from flask import Blueprint, render_template, request, redirect, url_for, flash, session,Response
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
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
                
                # Set session variables for OTP verification
                session["verify_email"] = email
                session["verification_purpose"] = "register"
                
                flash("Account created successfully! Please check your email for the OTP.", "success")
                return redirect(url_for("auth.verify_otp"))
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
                # Allow them to verify if they haven't yet
                session["verify_email"] = email
                session["verification_purpose"] = "register"
                return redirect(url_for("auth.verify_otp"))
                
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for("main.dashboard")) 
        else:
            flash("Invalid credentials given, try again", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

# Logout
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
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
        email = session.get("verify_email")
        
        if not email:
            flash("Session expired. Please try again.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()
        if user:
            if user.otp == otp:
                # Clear OTP after successful use to prevent reuse
                user.otp = None 
                
                purpose = session.get("verification_purpose")
                
                if purpose == "register":
                    user.is_verified = True
                    db.session.commit()
                    session.pop("verify_email", None)
                    session.pop("verification_purpose", None)
                    flash("Email verified successfully! Please login.", "success")
                    return redirect(url_for("auth.login"))
                
                elif purpose == "reset":
                    db.session.commit() # Save the cleared OTP
                    # Don't pop verify_email yet, reset_password needs it (or we pass it differently)
                    # Looking at reset.py, it uses session["verify_email"]
                    flash("Email verified successfully!", "success")
                    return redirect(url_for("reset.reset_password"))
                
                else:
                    # Fallback
                    user.is_verified = True
                    db.session.commit()
                    flash("Verified!", "success")
                    return redirect(url_for("auth.login"))

            flash("Invalid OTP", "danger")
        else:
            flash("User doesn't exist","danger")
    return render_template("verify_otp.html")


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    email = session.get("verify_email")
    if email:
        send_verification_email(email)
        flash("A new OTP has been sent to your email.", "info")
    else:
        flash("Session expired. Please try again.", "danger")
        return redirect(url_for("auth.login"))
    return redirect(url_for("auth.verify_otp"))

@auth_bp.route("/accountsettings", methods=["GET", "POST"])
@login_required
def account_settings():
    if request.method == "POST":
        username = request.form.get("username")
        image = request.files.get("profile_image")

        # update fields
        current_user.username = username
        if image and image.filename != "":
            current_user.local_image = image.read()
            current_user.image_mime = image.mimetype
        
        db.session.commit()
        flash("Account updated successfully", "success")
        return redirect(url_for("auth.account_settings"))
    return render_template("accountsettings.html", user=current_user)

@auth_bp.route("/user_image")
@login_required
def user_image():
    if current_user.local_image:
        return Response(current_user.local_image, mimetype=current_user.image_mime)
    elif current_user.profile_image:
        return redirect(current_user.profile_image)
    else:
        return redirect(url_for("static", filename="profile.png"))
#delete account
@auth_bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        password = request.form.get('password')
        if current_user.check_password(password):
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash('Your account has been deleted.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Incorrect password. Account not deleted.', 'danger')
    return render_template('delete_account.html')
