from flask import Blueprint, render_template, redirect, url_for, session
main_bp = Blueprint("main", __name__)
#landing page
@main_bp.route('/')
def index():
    return render_template("index.html")

#route to dashboard
@main_bp.route("/dashboard")
def dashboard():
    if "email" in session:
        return render_template("dashboard.html",email = session["email"])
    return redirect(url_for("main.index"))