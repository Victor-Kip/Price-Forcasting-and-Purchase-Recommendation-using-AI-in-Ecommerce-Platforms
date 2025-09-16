from flask import Flask, render_template,redirect,session,request,url_for,flash
from extensions import db
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = "my_secret_key"

#configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///genecomm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#initialize db with app
db.init_app(app)
from my_db_models import User, Product, PriceHistory, Forecast, Recommendation





#routes
#landing page
@app.route('/')
def index():
    return render_template("index.html")

#route to registration page and process registration details
@app.route('/register', methods = ["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if(password == confirm_password):
            user = User.query.filter_by(email = email).first()
            if user:
                flash("User already exists!", "warning")
                return redirect(url_for("register"))
                
            else:
                new_user = User(email = email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
        else:
            flash("Unmatched!", "danger")
            return redirect(url_for("register"))          

    return render_template("register.html")

# route to login page and process login request
@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        pass
    return render_template("login.html")

 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)