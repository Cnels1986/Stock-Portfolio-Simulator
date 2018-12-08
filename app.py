from flask import Flask, render_template, request, session, redirect, url_for, flash
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from MySQLdb import escape_string as thwart
from decimal import Decimal
import os
import requests
import json
import operator

app = Flask(__name__)
app.secret_key = "thisisthesecretkey2018"
mysql = MySQL()

name = ''
id = ''
info = ''

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'stocksdb'
app.config['MYSQL_DATABASE_HOST'] = '35.196.70.93'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Eagles717'
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

# functions are used to grab certain data from the database and returns it

def find_worth(id):
    s = []
    # gets the amount remaining in the user's wallet
    cursor.execute("SELECT money FROM Wallet JOIN Users on Wallet.user_id = Users.id WHERE Users.id = {}".format(id))
    temp = cursor.fetchone();
    money = temp[0]
    # gets user's portfolio and gets the current prices of their stocks
    portfolio = get_portfolio()
    # calculates user's total with in the app (wallet + stocks purchased)
    worth = 0
    for test in s:
        worth = worth + (test[1] * test[0][2])
    total = Decimal(worth) + money
    total = round(total,2)
    return float(total)

def get_portfolio():
    id = session['userid']
    # builds a list of the user's portfolio to send to the dashboard template
    s = []
    cursor.execute("SELECT Stocks.symbol, Stocks.name, amount, price, Portfolio.id FROM Portfolio JOIN Stocks on Stocks.id = Portfolio.stock_id WHERE user_id = {} ORDER BY Stocks.name".format(id))
    portfolio = cursor.fetchall()
    for stock in portfolio:
        price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(stock[0]))
        stockPrice = json.loads(price.text)
        p = round(stockPrice,2)
        stockTuple = (stock,p,round((p * stock[2]),2))
        s.append(stockTuple)
    return s

#####################

@app.route('/')
def temp():
    return redirect(url_for('login'))

#####################

@app.route('/dashboard')
@login_required
def index():
    user = session['userInfo']
    userName = session['name']
    money = session['wallet']
    total = find_worth(session['userid'])
    userList = []
    cursor.execute("SELECT id, username FROM Users WHERE id != {}".format(session['userid']))
    users = cursor.fetchall()
    for user in users:
        id = user[0]
        name = user[1]
        w = find_worth(id)
        thing = (name, float(w))
        userList.append(thing)
    userList.append((session['username'], total))
    userList.sort(key=lambda tup: tup[1])
    userList.reverse()

    return render_template("dashboard.html", user=user, money=money, portfolio=get_portfolio(), total=total, userName=userName, userList=userList)

#####################

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    error = None
    if request.method == "POST":
        # retrieves input from the login form
        username = request.form["userName"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM Users WHERE username = (%s)", thwart(username))
        # retrieves hashed password from the Users table
        user = cursor.fetchone()
        # user name does not exist within the Users table
        if user == None:
            error = "Incorrect Login Credentials"
        else:
            # verifies that password matches the hashed one in the database
            if sha256_crypt.verify(request.form["password"], user[2]):
                # creates the session variables that will be used throughout the app
                session['logged_in'] = True
                session['username'] = username
                session['userid'] = user[0]
                session['name'] = user[3]
                cursor.execute("SELECT money FROM Wallet JOIN Users on Wallet.user_id = Users.id WHERE Users.username = (%s)", session['username'])
                wallet = cursor.fetchone();
                session['wallet'] = float(wallet[0])
                session['userInfo'] = user
                session.permanent = False
                return redirect(url_for('index'))
            else:
                error = "Incorrect Login Credentials"

    return render_template('login.html', error=error)

#####################

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    session.clear()
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
            cursor.execute("INSERT INTO Users(username, password, name, admin) VALUES(%s, %s, %s, false)", (thwart(username), thwart(password), thwart(real_name)))
            # gets new users information
            cursor.execute("SELECT * FROM Users WHERE userName = (%s)", thwart(username))
            userID = cursor.fetchone()
            # adds $25000 to the users wallet
            cursor.execute("INSERT INTO Wallet(user_id, money) VALUES(%s, 25000.00)", (int(userID[0])))
            conn.commit()
            # sets the session so user is now logged in to the app
            session['logged_in'] = True
            session['username'] = username
            session['name'] = real_name
            session['userid'] = userID[0]
            session['wallet'] = 25000.00
            session['userInfo'] = userID
            session.permanent = False
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
        # uses IEX api to get stock price from the given symbol, if nothing found then its not an actual symbol
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
            stockInfo.append(round(stockPrice,2))
            stockInfo.append(companyInfo['exchange'])
            stockInfo.append(companyInfo['description'])
            # gather stock information to check the stocks table
            name = companyInfo['companyName']
            symbol = companyInfo['symbol']
            cursor.execute("SELECT * FROM Stocks WHERE symbol = (%s)", symbol)
            s = cursor.fetchone()
            # stock is currently not in the stocks table, adds new stock to table
            if s == None:
                cursor.execute("INSERT INTO Stocks(symbol, name) VALUES (%s, %s)", (symbol, name))
                conn.commit()
            cursor.execute("SELECT id FROM Stocks WHERE symbol = (%s)", symbol)
            stockid = cursor.fetchone()
            stockInfo.append(stockid[0])

            session['symbol'] = stockInfo[0]
            session['stockInfo'] = stockInfo
            return redirect(url_for('confirm'))
    m = session['wallet']
    cursor.execute("SELECT * FROM Stocks ORDER BY id DESC LIMIT 10")
    stocks = cursor.fetchall()
    userName = session['name']
    return render_template('buy.html', money=m, error=error, name=userName, stocks=stocks)

#####################

@app.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    error = ''
    # gets the information of the stock send and display within the template
    stockInfo = session['stockInfo']
    symbol = session['symbol']
    if request.method == 'POST':
        quantity = request.form['modalQuantity']
        price = stockInfo[2]
        stockid = stockInfo[5]
        money = session['wallet']
        cost = Decimal(quantity) * Decimal(price)
        if cost <= money:
            updatedMoney = money - round(float(cost),2)
            # adds entry to portfolio table of what stocks and how much user bought and at what price
            cursor.execute("INSERT INTO Portfolio(user_id, stock_id, amount, price) VALUES({},{},{},{})".format(session['userid'], stockid, quantity, float(price)))
            # updates the Wallet table with the new amount of money
            temp = round(float(updatedMoney),2)
            cursor.execute("UPDATE Wallet SET money={} WHERE user_id = {}".format(temp, session['userid']))
            conn.commit()
            session['wallet'] = temp
            return redirect(url_for('index'))
        else:
            error = "Not enough money to complete purchase"

    id = session['userid']
    m = session['wallet']
    prices = []
    dates = []
    # getting stock information for the last year to dynamically create a graph of the prices
    stockPriceInfo = requests.get("https://api.iextrading.com/1.0/stock/{}/chart/1y".format(symbol))
    PriceInfo = json.loads(stockPriceInfo.text)
    for a in PriceInfo:
        dates.append(a['date'])
        prices.append(round(a['close'],2))
    legend = "Stock Prices"
    userName = session['username']
    news = requests.get("https://api.iextrading.com/1.0/stock/{}/news/last/3".format(symbol))
    stockNews = json.loads(news.text)
    newsList = []
    for new in stockNews:
        newList = [new['url'],new['headline'],new['summary']]
        newsList.append(newList)
    return render_template("showstock.html", stockInfo=stockInfo, error=error, money=m, values=prices, labels=dates, legend=legend, name=userName, newsList=newsList)

#####################

@app.route('/sell')
@login_required
def sellstock():
    # s = []
    # cursor.execute("SELECT Portfolio.id, Stocks.symbol, Stocks.name, amount, price FROM Portfolio JOIN Stocks on Stocks.id = Portfolio.stock_id WHERE user_id = {} ORDER BY Stocks.name".format(session['userid']))
    # portfolio = cursor.fetchall()
    # # portfolio = session['portfolio']
    # for stock in portfolio:
    #     price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(stock[1]))
    #     stockPrice = json.loads(price.text)
    #     stockTuple = (stock, round(stockPrice,2))
    #     s.append(stockTuple)
    s = get_portfolio()
    money = session['wallet']
    userName = session['username']
    return render_template('sell.html', portfolio=s, name=userName, money=money)

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
            error = "Not enough owned"
            flash('Not enough stock owned')
            return redirect(url_for('sellstock'))
            # return render_template('sell.html', portfolio=get_portfolio(), name=session['username'], money=session['wallet'], error=error)
        else:
            # retrieves stock symbol that the user is selling
            cursor.execute("SELECT Stocks.symbol FROM Portfolio JOIN Stocks on Stocks.id = Portfolio.stock_id WHERE Portfolio.id = {}".format(portfolio_id))
            symbol = cursor.fetchone()
            # gets updated stock price
            price = requests.get("https://api.iextrading.com/1.0/stock/{}/price".format(symbol[0]))
            currentPrice = json.loads(price.text)
            # gets the user's id
            userId = session['userid']
            # calculates the price of the sale
            total = int(quantity) * currentPrice
            money = session['wallet']
            # updates money amount with sold stocks amount
            newMoney = total + money
            cursor.execute("UPDATE Wallet SET money = {} WHERE user_id = {}".format(newMoney, userId))
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

@app.route('/admin')
@login_required
def admin():
    cursor.execute("SELECT * FROM Users WHERE username = (%s)", session['username'])
    info = cursor.fetchone()
    # if the user is an admin goes to the admin page, if not will be redirected to the dashboard if they try the URL
    if info[4] == True:
        # selects all the users from the table other than the admin
        cursor.execute("SELECT id, username, name FROM Users WHERE username != (%s)", session['username'])
        users = cursor.fetchall();
        return render_template("admin.html", users=users)
    else:
        return redirect(url_for('index'))

####################

@app.route('/remove/<int:user_id>')
@login_required
def remove(user_id):
    cursor.execute("SELECT * FROM Users WHERE username = (%s)", session['username'])
    info = cursor.fetchone()
    # if the user is an admin goes to the admin page, if not will be redirected to the dashboard if they try the URL
    if info[4] == True:
        # deletes every instance of that user based on their user_id from the Wallet, Portfolio, and Users table
        cursor.execute('DELETE FROM Wallet WHERE user_id = (%s)', user_id)
        cursor.execute('DELETE FROM Portfolio WHERE user_id = (%s)', user_id)
        cursor.execute('DELETE FROM Users WHERE id = (%s)', user_id)
        conn.commit()
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('index'))

###################

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

name = ''
