from flask import Blueprint, render_template
import json

recommendation_bp = Blueprint("recommendation", __name__)

from flask_login import login_required

@recommendation_bp.route("/recommendation")
@login_required
def recommendation():
    # Load product data from DB
    from my_db_models import Product
    try:
        from model.inference import get_prediction
    except ImportError:
        # Fallback if model not loaded or import fails
        def get_prediction(*args): return None, "Model error"

    products = Product.query.all()
    recommendations = []
    for product in products:
        if not product.prices_list:
            continue
        last_price = product.prices_list[-1]
        
        # Get real forecast
        prediction, error = get_prediction(product.prices_list, product.description)
        
        if prediction:
            # Use the minimum price in the forecast horizon to find the best deal
            forecasted_price = min(prediction)
            price_drop = last_price - forecasted_price
            
            # Only recommend if there is a positive price drop
            if price_drop > 0:
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
