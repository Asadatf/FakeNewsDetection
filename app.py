from flask import Flask, request, render_template, redirect, url_for, session, g
from flask_caching import Cache
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import pickle
import re
import os

vector = pickle.load(open("models/vectorizer.pkl", 'rb'))
model = pickle.load(open("models/finalized_model.pkl", 'rb'))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:password123@localhost/fake'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    UserId = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        print(f"<User(UserId={self.UserId}, Email='{self.Email}', Password='{self.Password}')>")

# Configuration for Flask-Caching
app.config['CACHE_TYPE'] = 'simple'  # You can change this to other cache types like 'memcached' or 'redis'
cache = Cache(app)


# Secret key for session management
app.secret_key = os.urandom(24)

# Define a regular expression pattern to check for password strength
PASSWORD_PATTERN = re.compile(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}')

def is_strong_password(password):
    return bool(PASSWORD_PATTERN.fullmatch(password))

USERS = {
    'test@example.com': 'Test@1234',
    'user@example.com': 'P@ssword123'
}

@app.route("/")
def signup_get():
    print("In signup.html")
    return render_template("signup.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the password is strong
        if not is_strong_password(password):
            return render_template("signup.html", error="Password must be at least 8 characters long and contain at least one uppercase letter, one number, and one special character.")

        # Check if the email is already registered
        existing_user = User.query.filter_by(Email=email).first()
        if existing_user:
            return render_template("signup.html", error="Email already registered.")

        # Create a new user instance
        new_user = User(Email=email, Password=password)
        
        # Add the new user to the database session
        db.session.add(new_user)
        
        # Commit the transaction
        db.session.commit()

        session['logged_in'] = True
        session['user'] = email

        # Redirect to home page after signup
        return redirect(url_for('home'))

    # Render signup.html for GET requests
    return render_template("signup.html")


@app.route("/signin", methods=['GET', 'POST'])
@cache.cached(timeout=300)
def signin():
    print("Accessing signin route")
    print(request.method)
    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(Email=email).first()
        print("user")
        if user:
            print("found user")
            session['logged_in'] = True
            session['user'] = email
            return redirect(url_for('home'))  # Redirect to home page after successful signin
        else:
            # Return an error message for invalid credentials
            return render_template("signup.html", error="Invalid email or password.")

    else:
        if 'logged_in' in session:
            return redirect(url_for('home'))  # Redirect to home page if user is already logged in
        else:
            return render_template("signup.html")  # Render signup.html for signin pagege

@app.route("/home")
def home():
    print("g.user:", g.user)
    print("session['user']:", session.get('user'))
    if g.user:
        return render_template("index.html", user=session['user'])
    else:
        return redirect(url_for("signup_get"))

@app.route("/prediction", methods=['GET', 'POST'])
def prediction():
    if g.user:  # Check if user is logged in
        if request.method == "POST":
            news = str(request.form['news'])
            print(news)

            predict = model.predict(vector.transform([news]))[0]
            print(predict)

            return render_template("prediction.html", prediction_text="News headline is -> {}".format(predict))

        else:
            return render_template("prediction.html")
    else:
        return redirect(url_for('signin'))  # Redirect to signin page if user is not logged in

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")
    
@app.before_request
def before_request():
    g.user = session.get('user')

@app.route('/signout')
def signout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect(url_for('signup_get'))

if __name__ == '__main__':
    app.run(debug=True)