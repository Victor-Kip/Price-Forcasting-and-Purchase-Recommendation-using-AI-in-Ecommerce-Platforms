
from flask import Blueprint, request, render_template, session, redirect, url_for
import numpy as np
import json, os, logging
from my_db_models import User, Product, SearchLog
from extensions import db
from utils.subscription import check_forecast_limit, increment_forecast_count

predict_bp = Blueprint('predict', __name__, template_folder='../templates')
TIME_STEP = 12
PREDICTION_HORIZON = 5

try:
    from model.inference import model, scaler
except Exception as e:
    logging.error(f"Model/scaler import error: {e}")
    model = scaler = None

def get_prediction(product):
    if not product:
        return None, "Product not found."
    try:
        prices = product.prices_list
        if not prices or len(prices) != TIME_STEP:
            return None, f'Incorrect price data length for "{product.description}".'
        arr = np.array(prices, dtype=float).reshape(-1, 1)
        scaled = scaler.transform(arr)
        pred = model.predict(scaled.reshape(1, TIME_STEP, 1))
        final = pred.reshape(-1, 1)
        prediction = [round(float(val), 2) for val in final.flatten()]
        return prediction, None
    except Exception as e:
        logging.error(f"Prediction error for {product.description}: {e}")
        return None, "Prediction failed."

@predict_bp.route('/predict', methods=['POST', 'GET'])
def predict():
    prediction, error = None, None
    product_name_input = ""
    related_products = []
    
    if request.method == 'POST':
        product_name_input = request.form.get('product_name', '').strip()
        
        # Check subscription limit
        user_email = session.get('email')
        current_user_obj = None
        if user_email:
            current_user_obj = User.query.filter_by(email=user_email).first()
            if current_user_obj:
                if not check_forecast_limit(current_user_obj):
                    error = f"Daily forecast limit reached for your {current_user_obj.subscription_tier} plan. Please upgrade."
                    return render_template('dashboard.html', prediction=prediction, error=error, TIME_STEP=TIME_STEP, product_name=product_name_input, related_products=related_products)

        if not model or not scaler:
            error = "Model artifacts could not be loaded."
        elif not product_name_input:
            error = 'Please enter a product name or stock code.'
        else:
            product = Product.query.filter(
                (Product.description.ilike(f"%{product_name_input}%")) |
                (Product.code.ilike(f"%{product_name_input}%"))
            ).first()
            if product:
                # Related products logic
                first_word = product.description.split()[0].lower()
                related_products_db = Product.query.filter(
                    Product.description.ilike(f"{first_word}%"),
                    Product.ProductID != product.ProductID
                ).limit(3).all()
                for prod in related_products_db:
                    related_products.append({
                        'description': prod.description,
                        'prices': prod.prices_list,
                        'code': prod.code
                    })
                
                prediction, error = get_prediction(product)
                
                if prediction:
                    # Increment usage count if successful
                    if current_user_obj:
                        increment_forecast_count(current_user_obj)
                        
                    # --- DB update logic ---
                    if current_user_obj:
                        current_user_obj.last_searched_product = product.description
                        # Log the search
                        search_log = SearchLog(user_id=current_user_obj.UserID, product_id=product.ProductID)
                        db.session.add(search_log)
                        
                    product.predicted_price = prediction[0]
                    db.session.commit()
            else:
                error = f'Product "{product_name_input}" not found.'
                
    return render_template('dashboard.html', prediction=prediction, error=error, TIME_STEP=TIME_STEP, product_name=product_name_input, related_products=related_products)

@predict_bp.route('/forecast/<product_code>')
def forecast_product(product_code):
    # Check subscription limit
    user_email = session.get('email')
    current_user_obj = None
    if user_email:
        current_user_obj = User.query.filter_by(email=user_email).first()
        if current_user_obj:
            if not check_forecast_limit(current_user_obj):
                # We need to handle this gracefully, maybe redirect to dashboard with error
                # But since this is a GET request often linked, let's render the forecast page with an error
                return render_template('forecasts.html', error=f"Daily forecast limit reached for your {current_user_obj.subscription_tier} plan. Please upgrade.", prediction=None, product_name=None, comparison_name=None, comparison_prediction=None, related_products=[], historical_prices=[], zip=zip)

    product = Product.query.filter_by(code=product_code).first()
    prediction, error = get_prediction(product)
    
    if prediction and not error:
         if current_user_obj:
            increment_forecast_count(current_user_obj)

    product_name = product.description if product else None

    # Related products logic
    related_products = []
    historical_prices = []
    if product:
        first_word = product.description.split()[0].lower()
        related_products_db = Product.query.filter(
            Product.description.ilike(f"{first_word}%"),
            Product.ProductID != product.ProductID
        ).limit(3).all()
        for prod in related_products_db:
            related_products.append({
                'description': prod.description,
                'code': prod.code
            })
        try:
            historical_prices = product.prices_list
        except Exception:
            historical_prices = []

    comparison_name = None
    comparison_prediction = None
    compare_with_code = request.args.get('compare_with')

    if compare_with_code:
        comp_product = Product.query.filter_by(code=compare_with_code).first()
        if comp_product and comp_product.code != product_code:
            comparison_prediction, _ = get_prediction(comp_product)
            comparison_name = comp_product.description

    return render_template('forecasts.html', prediction=prediction, error=error, product_name=product_name, comparison_name=comparison_name, comparison_prediction=comparison_prediction, related_products=related_products, historical_prices=historical_prices, zip=zip)