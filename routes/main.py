from flask import Blueprint, render_template, redirect, url_for, session
from my_db_models import User, Product, Watchlist
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
        # Get user's watchlist products
        watchlist_items = []
        if user:
            items = Watchlist.query.filter_by(user_id=user.UserID).all()
            watchlist_items = [Product.query.get(item.product_id) for item in items]
    # Get all products
        all_products = Product.query.order_by(Product.ProductID.desc()).all()
        # Parse prices JSON for each product
        all_products_with_prices = []
        for product in all_products:
            try:
                prices_list = json.loads(product.prices)
            except Exception:
                prices_list = []
            all_products_with_prices.append({
                'ProductID': product.ProductID,
                'code': product.code,
                'description': product.description,
                'prices': prices_list
            })
        return render_template(
            "dashboard.html",
            email=session["email"],
            product_name=last_product,
            prediction=[last_prediction] if last_prediction is not None else None,
            watchlist=watchlist_items,
            all_products=all_products,
            all_products_with_prices=all_products_with_prices
        )
    return redirect(url_for("main.index"))