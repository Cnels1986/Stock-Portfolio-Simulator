from flask import Flask, render_template, request, session, redirect, url_for, flash
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from MySQLdb import escape_string as thwart
import os
import requests
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
mysql = MySQL()

name = ''
id = ''

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'stocksdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

#####################

# function checks the session loggin in status to see if user is logged in, if not it redirects them to the login page
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap

#####################

@app.route('/')
@login_required
def index():
    cursor.execute("SELECT username, name FROM Users WHERE username = (%s)", name)
    user = cursor.fetchone();
    cursor.execute("SELECT money FROM WALLET JOIN Users on Wallet.user_id = Users.id WHERE Users.username = (%s)", name)
    money = cursor.fetchone();
    return render_template("dashboard.html", user=user, money=money)

#####################

@app.route('/login', methods=['GET', 'POST'])
def login():
    errorName = None
    errorPass = None
    if request.method == "POST":
        # retrieves input from the login form
        username = request.form["userName"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM Users WHERE username = (%s)", thwart(username))
        # retrieves hashed password from the Users table
        user = cursor.fetchone()

        # user name does not exist within the Users table
        if user == None:
            errorName = "Username does not exist"
        else:
            if sha256_crypt.verify(request.form["password"], user[2]):
                session['logged_in'] = True
                session['username'] = username
                session.permanent = True
                flash("You are now logged in")
                global name
                name = username
                return redirect(url_for('index'))
            else:
                errorPass = "Incorrect password"

    return render_template('login.html', errorName=errorName, errorPass=errorPass)

#####################

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == "POST":
        # retrieves input from the register form
        username = request.form["userName"]
        password = sha256_crypt.encrypt(str(request.form["password"]))
        real_name = request.form["name"]

        # Queries database to see if the username already exists, they must be unique
        cursor.execute("SELECT * FROM Users WHERE username = (%s)", thwart(username))
        user = cursor.fetchone()

        # user name does not exist within the database, will now add the information to the Users table
        if user == None:
            # adds new user to Users table
            cursor.execute("INSERT INTO Users(username, password, name) VALUES(%s, %s, %s)", (thwart(username), thwart(password), thwart(real_name)))
            cursor.execute("SELECT * FROM Users WHERE userName = '{}'".format(username))
            userID = cursor.fetchone()
            cursor.execute("INSERT INTO Wallet(user_id, money) VALUES(%s, 25000)", (int(userID[0])))
            conn.commit()
            conn.close()
            # sets the session so user is now logged in to the app
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            flash("Thank you for registering")
            global name
            name = username
            return redirect(url_for('index'))
        else:
            error = "Username already exists"

    return render_template('register.html', error=error)

#####################
# https://api.iextrading.com/1.0/stock/aapl/price
# https://api.iextrading.com/1.0/stock/aapl/company

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buystock():
    error = None
    if request.method == 'POST':
        stock = request.form['searchStock']
        price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(stock))
        stockPrice = json.loads(price.text)
        company = requests.get("https://api.iextrading.com/1.0/stock/{}/company".format(stock))
        companyInfo = json.loads(company.text)

        stockInfo = []
        stockInfo.append(companyInfo['symbol'])
        stockInfo.append(companyInfo['companyName'])
        stockInfo.append(stockPrice)
        stockInfo.append(companyInfo['exchange'])
        stockInfo.append(companyInfo['description'])

        return render_template("showstock.html", stockInfo=stockInfo)
    return render_template('buy.html')

#####################

@app.route('/sell')
@login_required
def sellstock():
    return render_template('sell.html')

#####################

# the route clears the session and redirects user to the login page, thus logging the out
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You are now logged out")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

name = ''
