from extensions import db
from werkzeug.security import generate_password_hash,check_password_hash

#users tables
class User(db.Model):
    UserID = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50),unique = True,nullable = False)
    password_hash = db.Column(db.String(200))
    profile_image = db.Column(db.String(500))
    local_image = db.Column(db.LargeBinary)  
    image_mime = db.Column(db.String(50)) 
    is_verified = db.Column(db.Boolean, default=False)

    otp = db.Column(db.String(6),nullable = True)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    def __repr__(self):
        return f"<User {self.email}>"

#products table
class Product(db.Model):
    ProductID = db.Column(db.Integer,primary_key = True)
    Name = db.Column(db.String(100),nullable = False)
    Category = db.Column(db.String(50))
    Price = db.Column(db.Float,nullable = False)
    def __repr__(self):
        return f"<Product {self.name}>"

#price history table
class PriceHistory(db.Model):
    PriceID = db.Column(db.Integer,primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.ProductID'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='price_history')
    def __repr__(self):
        return f"<PriceHistory {self.product_id} - {self.date} - {self.price}>"

#forecasts
class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.ProductID'), nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)   # when prediction is made
    predicted_price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='forecasts')

    def __repr__(self):
        return f"<Forecast {self.product_id} - {self.forecast_date} - {self.predicted_price}>"
    
#recommendations
class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.ProductID'), nullable=False)
    reason = db.Column(db.String(200))  # e.g., "Based on your past searches"
    user = db.relationship('User', backref='recommendations')
    product = db.relationship('Product', backref='recommendations')

    def __repr__(self):
        return f"<Recommendation User:{self.user_id} Product:{self.product_id}>"