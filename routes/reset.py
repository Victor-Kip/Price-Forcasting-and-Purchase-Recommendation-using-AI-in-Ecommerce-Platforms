from flask import Blueprint,request,redirect,url_for,render_template,flash,session
reset_bp = Blueprint("reset", __name__, url_prefix="/reset")
from utils.email import send_reset_email
from my_db_models import User
from extensions import db
#password reset request
@reset_bp.route("/resetpasswordrequest",methods = ["GET","POST"],) 
def reset_password_request():
    if request.method == "POST":
        email = request.form["email"] 
        user = User.query.filter_by(email = email).first()
        if user: 
            send_reset_email(email) 
            flash("If your email exists in our system, you’ll get a reset link.", "info") 
            return redirect(url_for("auth.login")) 
        else:
            flash("The email entered doesn't exist,please try again","warning")
            return redirect(url_for("reset.reset_password_request"))
    return render_template("resetpasswordrequest.html")

#rest password page
@reset_bp.route("/resetpassword",methods = ["GET","POST"])
def reset_password():
    if request.method == "POST":
        email = session["email"]
        new_password = request.form["new_password"]
        confirm_new_password = request.form["confirm_new_password"]
        user = User.query.filter_by(email = email).first()
        if user:
            if new_password != confirm_new_password:
                flash("Passwords do not match","danger")
                return redirect(url_for("reset.reset_password"))
            if len(new_password) < 8:
                flash("Password must be at least 8 characters")
                return redirect(url_for("reset.reset_password"))
            user.set_password(new_password)
            db.session.commit()
            flash("Your password has been reset successfully","success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found","danger")            
            return redirect("reset.reset_password")
    return render_template("resetpassword.html")