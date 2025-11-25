
from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required, current_user
from my_db_models import User, Product, Watchlist
import json

main_bp = Blueprint("main", __name__)

#landing page
@main_bp.route('/')
def index():
    return render_template("index.html")

#route to dashboard
@main_bp.route("/dashboard")
@login_required
def dashboard():
    last_product = None
    last_prediction = None
    if current_user.last_searched_product:
        product = Product.query.filter_by(description=current_user.last_searched_product).first()
        if product:
            last_product = product.description
            last_prediction = product.predicted_price
    # Get user's watchlist products
    watchlist_items = []
    items = Watchlist.query.filter_by(user_id=current_user.UserID).all()
    watchlist_items = [Product.query.get(item.product_id) for item in items]
    # Get all products
    all_products = Product.query.order_by(Product.ProductID.desc()).all()
    # Parse prices JSON for each product
    all_products_with_prices = []
    for product in all_products:
        all_products_with_prices.append({
            'ProductID': product.ProductID,
            'code': product.code,
            'description': product.description,
            'prices': product.prices_list
        })
    return render_template(
        "dashboard.html",
        email=current_user.email,
        product_name=last_product,
        prediction=[last_prediction] if last_prediction is not None else None,
        watchlist=watchlist_items,
        all_products=all_products,
        all_products_with_prices=all_products_with_prices
    )

@main_bp.route('/search_products')
@login_required
def search_products():
    query = request.args.get('query', '').strip().lower()
    last_product = None
    last_prediction = None
    if current_user.last_searched_product:
        product = Product.query.filter_by(description=current_user.last_searched_product).first()
        if product:
            last_product = product.description
            last_prediction = product.predicted_price
    watchlist_items = []
    items = Watchlist.query.filter_by(user_id=current_user.UserID).all()
    watchlist_items = [Product.query.get(item.product_id) for item in items]
    
    # Filter products by query
    if query:
        all_products = Product.query.filter(
            (Product.description.ilike(f'%{query}%')) |
            (Product.code.ilike(f'%{query}%'))
        ).order_by(Product.ProductID.desc()).all()
    else:
        all_products = Product.query.order_by(Product.ProductID.desc()).all()
    
    all_products_with_prices = []
    for product in all_products:
        all_products_with_prices.append({
            'ProductID': product.ProductID,
            'code': product.code,
            'description': product.description,
            'prices': product.prices_list
        })

    # Compute related products based on the first search result
    related_products = []
    if all_products_with_prices:
        main_product = all_products_with_prices[0]
        main_desc = main_product['description']
        # Find products with similar words in description (excluding itself)
        for prod in all_products_with_prices[1:]:
            if any(word in prod['description'].lower() for word in main_desc.lower().split()):
                related_products.append(prod)
        # If not enough, fill with other products
        if len(related_products) < 3:
            related_products += [prod for prod in all_products_with_prices[1:] if prod not in related_products][:3-len(related_products)]

    return render_template(
        "dashboard.html",
        email=current_user.email,
        product_name=last_product,
        prediction=[last_prediction] if last_prediction is not None else None,
        watchlist=watchlist_items,
        all_products=all_products,
        all_products_with_prices=all_products_with_prices,
        related_products=related_products
    )

@main_bp.route('/product/<product_code>')
@login_required
def product_details(product_code):
    product = Product.query.filter_by(code=product_code).first()
    if not product:
        return redirect(url_for("main.dashboard"))
    # Find related products by matching words in description
    all_products = Product.query.order_by(Product.ProductID.desc()).all()
    related_products = []
    main_desc = product.description.lower()
    for prod in all_products:
        if prod.code == product_code:
            continue
        if any(word in prod.description.lower() for word in main_desc.split()):
            related_products.append({
                'code': prod.code,
                'description': prod.description,
                'prices': prod.prices_list
            })
        if len(related_products) >= 3:
            break
    # Render a product details template
    return render_template(
        "product_details.html",
        product={
            'code': product.code,
            'description': product.description,
            'prices': product.prices_list
        },
        related_products=related_products,
        email=current_user.email
    )