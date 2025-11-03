import os
import json
from extensions import db
from my_db_models import Product
from flask import Flask
from config import Config

# Path to the JSON file
JSON_PATH = os.path.join(os.path.dirname(__file__), 'model', 'product_price_data.json')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def import_products():
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)
    count = 0
    for code, info in data.items():
        # Check if product already exists
        if Product.query.filter_by(code=code).first():
            continue
        product = Product(
            code=code,
            description=info.get('description', ''),
            last_known_date=info.get('last_known_date', None),
            prices=json.dumps(info.get('prices', [])),
        )
        db.session.add(product)
        count += 1
    db.session.commit()
    print(f"Imported {count} products.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        import_products()
