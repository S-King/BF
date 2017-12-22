from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from helpers import *
import pprint # to show full html requests
# import sqlite3 # to control transactions/rollbacks    #### Deprecated, switching to MySQL ####
#from flask_mysqldb import MySQL
import MySQLdb
import datetime # for database timestamps
from cryptocompare_helpers import * # Helper functions for cryptocompare
from rss_helpers import * # Helper functions for rss feeds
###### Set up schedules ######
import time     # Library for scheduling time based events
import atexit   # Library for scheduling time based events
from apscheduler.schedulers.background import BackgroundScheduler  # Library for scheduling time based events
from apscheduler.triggers.interval import IntervalTrigger  # Library for scheduling time based events
from app_schedules import *
##############################
import logging
logging.basicConfig(filename='visitor.log',level=logging.WARNING) # Set to only record warnings since I don't want every request's info clogging up logs

if __name__ == '__main__':
    main()

# delete later #
# configure application, instance_relative_config=True allows us to use instance folders for sensitive data
app = Flask(__name__,instance_relative_config=True) 
#app.config.from_object('config')  # Call original config file
app.config.from_pyfile('config.py') # Call instance folder config file, this can overwrite the object variables if they are the same name

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
 
# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

## OLD DB INFO ##
# MySQL configurations
# mysql = MySQL()
# app.config['MYSQL_USER'] = 'blockroot'
# app.config['MYSQL_PASSWORD'] = 'pass'
# app.config['MYSQL_DB'] = 'Blockfund'
# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_PORT'] = 3306
# mysql.init_app(app)
Session(app)

# This creates a connection and tears it down after every request
@app.teardown_appcontext
def close_db(error):
    # Closes the database again at the end of the request.
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()
        
def get_db():
    # Opens a new database connection if there is none yet for the current application context.
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Blockfund', local_infile = 1)
    return g.mysql_db        


## Basic Routing Structure ##
@app.route("/")
#@login_required
def index():
    log_msg = 'Index visited by IP: {}'.format(request.remote_addr)
    logging.warning(log_msg)
    print(log_msg)
    
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    print("IP: {}".format(ip))
        
    
    
    # loadDashboardChartsJson()
    cursor = get_db().cursor()
    # cursor.execute("Select * from btcusd_instantprices order by date desc limit 1;")
    cursor.execute("SELECT (@row_number:=(@row_number + 1)%2) AS newsbucket, PK FROM NewsFeed,(SELECT @row_number:=0) AS t limit 20;") # divide news articles into two bucket, limit 10 articles for each widget
    news = list(cursor.fetchall())

    # btc_price = results[0][2]
    return render_template('index_nwelayout.html', 
        # btcprice='{:,.2f}'.format(btc_price)
        news_articles = news        
        )


@app.route("/email")
#@login_required
def email():
    return render_template('email.html')


@app.route("/icons.html")
@app.route("/icons")
#@login_required
def icons():
    return render_template('icons.html')


@app.route("/apicall")
#@login_required
def api_call():
    client = Client(app.config["COINBASE_API_KEY"], app.config["COINBASE_API_SECRET"])
    # client._make_api_object(client._get('v2', 'prices', 'ETH-USD', 'historic'), APIObject)
    currency_code = 'ETH' 
    
    #price = client.get_spot_price(currency=currency_code)
    price = client.get_spot_price(currency_pair= "ETH-USD")
    print(price)
    

    return render_template('index.html')



@app.route("/login", methods=["GET", "POST"])
def login():
    log_msg = 'Login visited by IP: {}'.format(request.remote_addr)
    logging.warning(log_msg)
    print(log_msg)    
    

    """Log user in."""
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        print("HERE")

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # # query database for username
        # db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Blockfund', local_infile = 1)
        #     # Check if connection was successful
        #     if (!db):
        #         print("Connection unsuccessful")
        #         return -1
        #     else:
        #     # Terminate
        #     cursor = db.cursor()
        #     cursor.execute("Select * from Blockfund.users where username = :username")
        #     results = list(cursor.fetchall())        
        # rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")
 
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
    
    
    
    return render_template('login.html')




@app.route("/markets")
#@login_required
def markets():
    cursor = get_db().cursor()
    cursor.execute("SET @row_number = 0;")
    cursor.execute("SELECT (@row_number := @row_number +1) AS rownum, symbol, marketcap, price, volume24hr, supply, percentchange24hr, date FROM `marketcaps` WHERE volume24hr <> 0 ORDER BY marketcap DESC LIMIT 25;")
    results = cursor.fetchall()
    # print(results)

    return render_template('markets.html', 
        marketcaps=results)    
    

@app.route("/invest", methods=["GET", "POST"])
#@login_required
def invest():
    test_list = [['Individual Trade', 'BTC', 'Bitcoin', '5200.54', '0.01231', '200.32', '2017-12-14 20:45:31','17500.21', '998.12'],['Portfolio Total', 'BTC', 'Bitcoin', '5200.54', '0.01231', '200.32', '2017-12-14 20:45:31','17500.21', '998.12']]
    test_txn_list = [['BTC', '5900.12', '5.223', '25000.12', '2017-12-20 20:45:31'], ['BTC', '11900.12', '1.223', '25000.12', '2017-12-24 20:45:31']]
    
    
    return render_template('invest_test.html', 
    portfolio_list=test_list, 
    txn_list=test_txn_list, 
    cash=usd(9210.11), 
    total_value=usd(1117.21)
    )
    
    
@app.route("/invest_test", methods=["GET", "POST"])
#@login_required
def invest_test():
    test_list = [['Individual Trade', 'BTC', 'Bitcoin', '5200.54', '0.01231', '200.32', '2017-12-14 20:45:31','17500.21', '998.12'],['Portfolio Total', 'BTC', 'Bitcoin', '5200.54', '0.01231', '200.32', '2017-12-14 20:45:31','17500.21', '998.12']]
    test_txn_list = [['BTC', '5900.12', '5.223', '25000.12', '2017-12-20 20:45:31'], ['BTC', '11900.12', '1.223', '25000.12', '2017-12-24 20:45:31']]
    
    
    return render_template('invest_test.html', 
    portfolio_list=test_list, 
    txn_list=test_txn_list, 
    cash=usd(9210.11), 
    total_value=usd(1117.21)
    )    
    

@app.route("/education", methods=["GET"])
#@login_required
def education():
    return render_template('education.html')



@app.route("/charts", methods=["GET"])
#@login_required
def charts():
    return render_template('charts.html')



#***************************************************************************
#                              SCHEDULED JOBS                              *
#***************************************************************************
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(          
    func=lambda: syncInstantPrices(['BTC'], ['USD']),      # Must use lambda to pass function referencewith parameters otherwise function fires on app start
    trigger='cron',
    year='*', month='*', day="*", week='*', day_of_week='*', hour='*', minute="*", second="*/30");
    
scheduler.add_job(          
    func=lambda: syncMarkets(),      # Must use lambda to pass function referencewith parameters otherwise function fires on app start
    trigger='cron',
    year='*', month='*', day="*", week='*', day_of_week='*', hour='*', minute="32", second="5");    
    
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Example scheduler for timed tasks
# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=print_date_time,
#     trigger=IntervalTrigger(minutes=1),
#     id='printing_job',
#     name='Print date and time every five seconds',
#     replace_existing=True)
    
# scheduler.add_job(            ## Shit works, was just testing it
#     # Cant figure out how to pass mysql
#     # need to figure it out how to get app reference object
#     # info here: http://flask-mysqldb.readthedocs.io/en/latest/
#     func=lambda: add_daily_price_to_db('BTC'),      # Must use lambda to pass function referencewith parameters otherwise function fires on app start
#     trigger='cron',
#     year='*', month='*', day="*", week='*', day_of_week='*', hour='*', minute="*", second="*/5");
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
#############################
# scheduler.add_job(            ## Shit works, was just testing it
#     # Cant figure out how to pass mysql
#     # need to figure it out how to get app reference object
#     # info here: http://flask-mysqldb.readthedocs.io/en/latest/
#     func=lambda: syncDailyPrices(),      # Must use lambda to pass function referencewith parameters otherwise function fires on app start
#     trigger='cron',
#     year='*', month='*', day="*", week='*', day_of_week='*', hour='*', minute="*/5");
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
############################

# Example of what logging looks like:
    # logging.basicConfig(filename='visitor.log',level=logging.DEBUG)
    # logging.debug('This message should go to the log file')
    # logging.info('So should this')
    # logging.warning('And this, too')
# What will show up in the log file:
    # DEBUG:root:This message should go to the log file
    # INFO:root:So should this
    # WARNING:root:And this, too
    
# Logging levels of severity are 
# CRITICAL	50
# ERROR	    40
# WARNING	30
# INFO	    20
# DEBUG	    10
# NOTSET	0






