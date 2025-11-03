from flask import Blueprint, request, render_template, session
import numpy as np
import json, os, logging
from my_db_models import User, Product
from extensions import db

predict_bp = Blueprint('predict', __name__, template_folder='../templates')
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model')
DATA_PATH = os.path.join(MODEL_DIR, 'product_price_data.json')
TIME_STEP = 12
PREDICTION_HORIZON = 5

try:
    from model.inference import model, scaler
except Exception as e:
    logging.error(f"Model/scaler import error: {e}")
    model = scaler = None

# Load product data
try:
    with open(DATA_PATH, 'r') as f:
        PRODUCT_DATA = json.load(f)
except Exception as e:
    logging.error(f"Product data load error: {e}")
    PRODUCT_DATA = {}

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
            found = None
            for code, info in PRODUCT_DATA.items():
                if product_name_input.lower() == info.get('description', '').lower() or product_name_input.upper() == code.upper():
                    found = info
                    break
            # Related products logic
            if product_name_input:
                first_word = product_name_input.split()[0].lower()
                for code, info in PRODUCT_DATA.items():
                    desc = info.get('description', '').lower()
                    if desc.startswith(first_word) and (not found or desc != found.get('description', '').lower()):
                        related_products.append(info)
                        if len(related_products) >= 3:
                            break
            if not found:
                error = f'Product "{product_name_input}" not found.'
            else:
                prices = found.get('prices')
                if not prices or len(prices) != TIME_STEP:
                    error = f'Incorrect price data length for "{product_name_input}".'
                else:
                    try:
                        arr = np.array(prices, dtype=float).reshape(-1, 1)
                        scaled = scaler.transform(arr)
                        pred = model.predict(scaled.reshape(1, TIME_STEP, 1))
                        final = pred.reshape(-1, 1)
                        prediction = [round(float(val), 2) for val in final.flatten()]
                        # --- DB update logic ---
                        # Update User.last_searched_product
                        user_email = session.get('email')
                        if user_email:
                            user = User.query.filter_by(email=user_email).first()
                            if user:
                                user.last_searched_product = product_name_input
                                db.session.commit()
                        # Update Product.predicted_price if not exists
                        product_db = Product.query.filter_by(Name=found.get('description')).first()
                        if not product_db:
                            # Add product with predicted price
                            new_product = Product(Name=found.get('description'), Price=prices[-1], predicted_price=prediction[0])
                            db.session.add(new_product)
                            db.session.commit()
                        # If product exists, skip
                    except Exception as e:
                        logging.error(f"Prediction error: {e}")
                        error = 'Prediction failed.'
    return render_template('dashboard.html', prediction=prediction, error=error, TIME_STEP=TIME_STEP, product_name=product_name_input, related_products=related_products)
