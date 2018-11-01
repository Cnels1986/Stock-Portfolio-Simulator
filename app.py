from flask import Flask, render_template, request, session, redirect, url_for, flash
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import os

app = Flask(__name__)
mysql = MySQL()

name = ''

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'stocksdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template("dashboard.html")

@app.route('/login')
def login():
    return render_template("login.html")

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
            # session['logged_in'] = True
            # session['username'] = username
            # session.permanent = True
            # flash("Thank you for registering")
            return redirect(url_for('index'))
        else:
            error = "Username already exists"

    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    return "This is the logout"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

name = ''
