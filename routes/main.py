from flask import Blueprint, render_template, redirect, url_for, session
from my_db_models import User, Product
import json
main_bp = Blueprint("main", __name__)
#landing page
@main_bp.route('/')
def index():
    return render_template("index.html")

#route to dashboard
@main_bp.route("/dashboard")
def dashboard():
    if "email" in session:
        user = User.query.filter_by(email=session["email"]).first()
        last_product = None
        last_prediction = None
        if user and user.last_searched_product:
            product = Product.query.filter_by(description=user.last_searched_product).first()
            if product:
                last_product = product.description
                last_prediction = product.predicted_price
        return render_template(
            "dashboard.html",
            email=session["email"],
            product_name=last_product,
            prediction=[last_prediction] if last_prediction is not None else None
        )
    return redirect(url_for("main.index"))