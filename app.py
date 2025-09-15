from flask import Flask, render_template,redirect,session,request
from flask_sqlalchemy import SQLALchemy
from models import User,Product,PriceHistory,Forecast,Recommendation

app = Flask(__name__)
app.secret_key = "my_secret_key"

#configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///genecomm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLALchemy(app)



#routes
#landing page
@app.route('/')
def index():
    return render_template("index.html")

#route to register page
@app.route('/register')
def register():
    return render_template("register.html")

# route to login page and process login request
@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        pass
    return render_template("login.html")

 

if __name__ == '__main__':
    app.run(debug=True)