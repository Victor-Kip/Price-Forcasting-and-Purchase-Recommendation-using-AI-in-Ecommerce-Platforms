from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from my_db_models import User, SearchLog, Product
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('main.dashboard'))

    # Most searched products
    # Group by product_id, count, order by count desc
    most_searched = db.session.query(
        Product.description, 
        func.count(SearchLog.id).label('search_count')
    ).join(SearchLog, SearchLog.product_id == Product.ProductID)\
    .group_by(Product.ProductID)\
    .order_by(func.count(SearchLog.id).desc())\
    .limit(10).all()

    # Most active users
    # Based on forecast_count
    most_active_users = User.query.order_by(User.forecast_count.desc()).limit(10).all()

    return render_template('admin_dashboard.html', most_searched=most_searched, most_active_users=most_active_users)
