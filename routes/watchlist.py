from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from extensions import db
from my_db_models import Watchlist, Product, User

watchlist_bp = Blueprint('watchlist', __name__)

@watchlist_bp.route('/watchlist/add/<int:product_id>', methods=['POST'])
def add_to_watchlist(product_id):
    user_id = session.get('UserID')
    if not user_id:
        flash('You must be logged in to add to watchlist.', 'warning')
        return redirect(url_for('auth.login'))
    existing = Watchlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not existing:
        item = Watchlist(user_id=user_id, product_id=product_id)
        db.session.add(item)
        db.session.commit()
        flash('Product added to your watchlist!', 'success')
    else:
        flash('Product is already in your watchlist.', 'info')
    return redirect(request.referrer or url_for('main.dashboard'))

@watchlist_bp.route('/watchlist/remove/<int:product_id>', methods=['POST'])
def remove_from_watchlist(product_id):
    user_id = session.get('UserID')
    if not user_id:
        flash('You must be logged in to remove from watchlist.', 'warning')
        return redirect(url_for('auth.login'))
    item = Watchlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Product removed from your watchlist.', 'success')
    else:
        flash('Product not found in your watchlist.', 'info')
    return redirect(request.referrer or url_for('main.dashboard'))

@watchlist_bp.route('/watchlist')
def view_watchlist():
    user_id = session.get('UserID')
    if not user_id:
        flash('You must be logged in to view your watchlist.', 'warning')
        return redirect(url_for('auth.login'))
    items = Watchlist.query.filter_by(user_id=user_id).all()
    products = [Product.query.get(item.product_id) for item in items]
    return render_template('watchlist.html', products=products)
