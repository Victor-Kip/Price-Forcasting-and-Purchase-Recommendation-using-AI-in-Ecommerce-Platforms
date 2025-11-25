from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from flask_login import login_required, current_user
from extensions import db
from my_db_models import Watchlist, Product, User

watchlist_bp = Blueprint('watchlist', __name__)

@watchlist_bp.route('/watchlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_watchlist(product_id):
    existing = Watchlist.query.filter_by(user_id=current_user.UserID, product_id=product_id).first()
    if not existing:
        item = Watchlist(user_id=current_user.UserID, product_id=product_id)
        db.session.add(item)
        db.session.commit()
        flash('Product added to your watchlist!', 'success')
    else:
        flash('Product is already in your watchlist.', 'info')
    return redirect(request.referrer or url_for('main.dashboard'))

@watchlist_bp.route('/watchlist/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_watchlist(product_id):
    item = Watchlist.query.filter_by(user_id=current_user.UserID, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Product removed from your watchlist.', 'success')
    else:
        flash('Product not found in your watchlist.', 'info')
    return redirect(request.referrer or url_for('main.dashboard'))

@watchlist_bp.route('/watchlist')
@login_required
def view_watchlist():
    items = Watchlist.query.filter_by(user_id=current_user.UserID).all()
    products = [Product.query.get(item.product_id) for item in items]
    return render_template('watchlist.html', products=products)
