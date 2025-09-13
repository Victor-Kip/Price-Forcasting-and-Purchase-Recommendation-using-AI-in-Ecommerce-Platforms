from flask import Flask, render_template

app = Flask(__name__)

#routes
#landing page
@app.route('/')
def index():
    return render_template("index.html")

#register page
@app.route('/register')
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)