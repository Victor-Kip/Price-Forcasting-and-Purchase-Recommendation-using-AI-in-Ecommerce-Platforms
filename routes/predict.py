from flask import Blueprint, request, render_template, session,redirect,url_for
import numpy as np
import json, os, logging
from my_db_models import User, Product
from extensions import db

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
        prices = json.loads(product.prices)
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
                        'prices': json.loads(prod.prices),
                        'code': prod.code
                    })
                prediction, error = get_prediction(product)
                if prediction:
                    # --- DB update logic ---
                    user_email = session.get('email')
                    if user_email:
                        user = User.query.filter_by(email=user_email).first()
                        if user:
                            user.last_searched_product = product.description
                            db.session.commit()
                    product.predicted_price = prediction[0]
                    db.session.commit()
            else:
                error = f'Product "{product_name_input}" not found.'
    return render_template('dashboard.html', prediction=prediction, error=error, TIME_STEP=TIME_STEP, product_name=product_name_input, related_products=related_products)

@predict_bp.route('/forecast/<product_code>')
def forecast_product(product_code):
    product = Product.query.filter_by(code=product_code).first()
    prediction, error = get_prediction(product)
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
            historical_prices = json.loads(product.prices)
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