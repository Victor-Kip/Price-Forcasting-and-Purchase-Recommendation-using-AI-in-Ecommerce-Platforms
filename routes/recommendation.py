from flask import Blueprint, render_template
import json

recommendation_bp = Blueprint("recommendation", __name__)

from flask_login import login_required

@recommendation_bp.route("/recommendation")
@login_required
def recommendation():
    # Load product data from DB
    from my_db_models import Product
    products = Product.query.all()
    recommendations = []
    for product in products:
        if not product.prices_list:
            continue
        last_price = product.prices_list[-1]
        # Simulate a forecasted price drop (replace with your model's prediction)
        forecasted_price = last_price - 0.1  # Replace with real forecast
        price_drop = last_price - forecasted_price
        recommendations.append({
            "code": product.code,
            "description": product.description,
            "last_price": last_price,
            "forecasted_price": forecasted_price,
            "price_drop": price_drop
        })
    recommendations.sort(key=lambda x: x["price_drop"], reverse=True)
    top_recommendations = recommendations[:5]
    return render_template("recommendation.html", recommendations=top_recommendations)
