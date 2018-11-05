from flask import Flask, render_template, request, session, redirect, url_for, flash
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from MySQLdb import escape_string as thwart
from decimal import Decimal
import os
import requests
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
mysql = MySQL()

name = ''
id = ''
info = ''

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

####################

def get_money(userId):
    cursor.execute("SELECT money FROM Wallet WHERE user_id = {}".format(userId))
    money = cursor.fetchone()
    return money[0]

def get_user_id():
    cursor.execute("SELECT id FROM Users WHERE username = (%s)", name)
    userId = cursor.fetchone()
    return userId[0]

#####################

@app.route('/')
@login_required
def index():
    s = []
    cursor.execute("SELECT id, username, name FROM Users WHERE username = (%s)", name)
    user = cursor.fetchone();
    cursor.execute("SELECT money FROM Wallet JOIN Users on Wallet.user_id = Users.id WHERE Users.username = (%s)", name)
    temp = cursor.fetchone();
    money = round(Decimal(temp[0]), 2)
    cursor.execute("SELECT Stocks.symbol, Stocks.name, amount, price FROM Portfolio JOIN Stocks on Stocks.id = Portfolio.stock_id WHERE user_id = {}".format(user[0]))
    portfolio = cursor.fetchall()
    for stock in portfolio:
        price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(stock[0]))
        stockPrice = json.loads(price.text)
        stockTuple = (stock,round(stockPrice,2))
        s.append(stockTuple)
    return render_template("dashboard.html", user=user, money=money, portfolio=s)

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
            cursor.execute("INSERT INTO Wallet(user_id, money) VALUES(%s, 25000.00)", (int(userID[0])))
            conn.commit()
            # conn.close()
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

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buystock():
    error = ''
    if request.method == 'POST':
        stock = request.form['searchStock']
        price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(stock))
        if price.status_code == 404:
            error = "Stock symbol does not exist"
        else:
            stockPrice = json.loads(price.text)
            company = requests.get("https://api.iextrading.com/1.0/stock/{}/company".format(stock))
            companyInfo = json.loads(company.text)

            # creates a list to send to the stocks page, stores the symbol, name, price, exchange, description
            stockInfo = []
            stockInfo.append(companyInfo['symbol'])
            stockInfo.append(companyInfo['companyName'])
            stockInfo.append(stockPrice)
            stockInfo.append(companyInfo['exchange'])
            stockInfo.append(companyInfo['description'])

            # gather stock information to check the stocks table
            name = companyInfo['companyName']
            symbol = companyInfo['symbol']
            cursor.execute("SELECT * FROM Stocks WHERE symbol = (%s)", symbol)
            s = cursor.fetchone()
            # stock is currently not in the stocks table
            if s == None:
                cursor.execute("INSERT INTO Stocks(symbol, name) VALUES (%s, %s)", (symbol, name))
                conn.commit()
                # conn.close()


            # cursor.execute("SELECT * FROM Stocks ORDER BY id DESC LIMIT 10")
            # latestStocks = cursor.fetchall()
            # print(latestStocks)
            global info
            info = stockInfo
            return redirect(url_for('confirm'))
        # return render_template("showstock.html", stockInfo=stockInfo)
    id = get_user_id()
    m = get_money(id)
    return render_template('buy.html', money=m, error=error)

#####################

@app.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    error = ''
    # gets the information of the stock send and display within the template
    global info
    stockInfo = info
    if request.method == 'POST':
        quantity = request.form['stockQuantity']
        symbol = stockInfo[0]
        price = stockInfo[2]
        cursor.execute("SELECT money FROM WALLET JOIN Users on Wallet.user_id = Users.id WHERE Users.username = (%s)", name)
        money = cursor.fetchone()
        cost = Decimal(quantity) * Decimal(price)

        if cost <= money[0]:
            cursor.execute("SELECT id FROM Stocks WHERE symbol = (%s)", symbol)
            stockId = cursor.fetchone()
            updatedMoney = money[0] - cost
            cursor.execute("SELECT id FROM Users WHERE username = (%s)", name)
            userId = cursor.fetchone()
            cursor.execute("SELECT * FROM Portfolio JOIN Stocks ON Portfolio.stock_id = Stocks.id WHERE Portfolio.user_id = {}".format(userId[0]))
            portfolioCheck = cursor.fetchone()
            print(portfolioCheck)
            # adds entry to portfolio table of what stocks and how much user bought and at what price
            cursor.execute("INSERT INTO Portfolio(user_id, stock_id, amount, price) VALUES({},{},{},{})".format(userId[0], stockId[0], quantity, float(price)))
            conn.commit()
            # updates the Wallet table with the new amount of money
            temp = float(updatedMoney)
            cursor.execute("UPDATE Wallet SET money=(%f) WHERE user_id = (%i)" % (temp, userId[0]))
            conn.commit()
            return redirect(url_for('index'))
        else:
            error = "Not enough money to complete purchase"

    id = get_user_id()
    m = get_money(id)
    return render_template("showstock.html", stockInfo=stockInfo, error=error, money=m)

#####################

@app.route('/sell')
@login_required
def sellstock():
    s = []
    cursor.execute("SELECT id FROM Users WHERE username = (%s)", name)
    userId = cursor.fetchone()
    cursor.execute("SELECT Portfolio.id, Stocks.symbol, Stocks.name, amount, price FROM Portfolio JOIN Stocks on Stocks.id = Portfolio.stock_id WHERE user_id = {}".format(userId[0]))
    portfolio = cursor.fetchall()
    for stock in portfolio:
        price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(stock[1]))
        stockPrice = json.loads(price.text)
        stockTuple = (stock, round(stockPrice,2))
        s.append(stockTuple)
    money = get_money(userId[0])
    return render_template('sell.html', portfolio=s, name=name, money=money)

#####################

@app.route('/confirmsale/<username>/<portfolio_id>', methods=['POST'])
@login_required
def sell(username, portfolio_id):
    error = ''
    if request.method == "POST":
        quantity = request.form['sellStock']
        cursor.execute("SELECT amount FROM Portfolio WHERE id = {}".format(portfolio_id))
        owned = cursor.fetchone()
        if int(quantity) > owned[0]:
            return "YOU DON'T OWN THAT MANY"
        else:
            # retrieves stock symbol that the user is selling
            cursor.execute("SELECT Stocks.symbol FROM Portfolio JOIN Stocks on Stocks.id = Portfolio.stock_id WHERE Portfolio.id = {}".format(portfolio_id))
            symbol = cursor.fetchone()
            # gets updated stock price
            price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(symbol[0]))
            currentPrice = json.loads(price.text)
            # gets the user's id
            cursor.execute("SELECT id FROM Users WHERE username = (%s)", username)
            temp = cursor.fetchone()
            userId = temp[0]
            # calculates the price of the sale
            total = int(quantity) * currentPrice
            cursor.execute("SELECT money FROM Wallet WHERE id = {}".format(userId))
            money = cursor.fetchone()
            # updates money amount with sold stocks amount
            newMoney = Decimal(total) + money[0]
            cursor.execute("UPDATE WALLET SET money = {} WHERE user_id = {}".format(newMoney, userId))
            newAmount = owned[0] - int(quantity)

            if newAmount == 0:
                cursor.execute("DELETE FROM Portfolio WHERE id = {}".format(portfolio_id))
                conn.commit()
            else:
                cursor.execute("UPDATE Portfolio SET amount = {} WHERE id = {}".format(newAmount, portfolio_id))
                conn.commit()

    return redirect(url_for('index'))

#####################

# the route clears the session and redirects user to the login page, thus logging the out
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You are now logged out")
    return redirect(url_for('login'))

#####################

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

name = ''
