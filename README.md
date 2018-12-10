# Stock Portfolio Simulator

This application will allow users to sign up and register for it. Once signed out, each user will be given $25,000 which will be used to buy whatever stocks they want. Using the IEX API, the app will be able to retrieve the up to date price for whatever stock the user enters. Users will also be able to sell their stocks at the current price and purchase more if desired. The goal being that each user will be trying to make the most profit while competing with each other. The app's dashboard will contain the information of the user, the stocks they own, and how the compare to the other users of the app.

## Getting Started

Deployed:
https://stock-portfolio-simulator.herokuapp.com

### Prerequisites

Requires Python 3 to be installed to use. Follow the Installing section to get the correct dependencies for the app. Internet access is also required to access the remote database and use the IEX API to get the stock information.

### Installing

Dependencies must be installed before the application can work properly.

```
export FLASK_APP=app.py
export FLASK_ENV=development
. venv/bin/activate
$pip install -r requirements.txt
```

This will create a virtual environment locally and will install the needed dependencies found in the requirements.txt file

## Usage

Users will be required to sign up for the app in order to use it. Once registered/logged in, users will be able to buy and sell stocks based on their current prices on the market. The purpose of this application is to let users try and compete with one another to see who can make the most profits from their original $25,000. The Buy Stocks page lets user search for stocks based on their symbol and then buy those stocks as long as they have enough cash available. The Sell Stocks pages lets the user sell any of the stocks they've bought at their current price.

## Running the tests

To run the automated tests use the command:

```
python3 test.py
```

## Credit

This app uses the IEX trading API to retrieve all the data on each of the stocks. API documentation can be found at:

https://iextrading.com/developer/docs/

## Author

Chris Nelson 2018
