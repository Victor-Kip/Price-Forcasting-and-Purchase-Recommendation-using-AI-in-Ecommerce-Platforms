from flask import Blueprint,request,redirect,url_for,render_template,flash
reset_bp = Blueprint("reset", __name__, url_prefix="/reset")
from utils.email import send_verification_email
from my_db_models import User
#password reset 
@reset_bp.route("/resetpassword",methods = ["GET","POST"]) 
def reset_password_request():
    if request.method == "POST":
        email = request.form["email"] 
        user = User.query.filter_by(email = email).first()
        if user: 
            send_verification_email(user) 
            flash("If your email exists in our system, you’ll get a reset link.", "info") 
            return redirect(url_for("auth.login")) 
        return render_template("resetpassword.html")