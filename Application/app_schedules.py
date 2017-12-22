import MySQLdb
from flask import Flask, flash, redirect, render_template, request, session, url_for
import cryptocompare
# from flask_mysqldb import MySQL
# ###### Set up schedules ######
import time     # Library for scheduling time based events
import datetime # db conversions
# import atexit   # Library for scheduling time based events
# from apscheduler.schedulers.background import BackgroundScheduler  # Library for scheduling time based events
# from apscheduler.triggers.interval import IntervalTrigger  # Library for scheduling time based events

## Can't get the right object reference so stopping here for now
# from flask import g
# mysql = MySQL()
# mysql.init_app(g)
#app = Flask("application")


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
    
def printit(sometext):
    print("this happens every")
    print(sometext)


# Need to add try catch blocks and XSS protection
# def add_daily_price_to_db(symbol):
#     # cryptocompare.get_historical_price('BTC', 'USD', datetime.datetime(2017,11,17))  # Get a day in time
#     # cryptocompare.get_price('BTC',curr='USD',full   =True)  # Get all current info
#     API_Response = cryptocompare.get_price(['BTC','ETH'],'USD')  # --> {'BTC': {'USD': 7747.57}, 'ETH': {'USD': 334.77}}

#     # Connect to the MySQL database
#     db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Blockfund')
#     # Check if connection was successful
#     if (db):
#     # Carry out normal procedure 
#         print("Connection successful")
#     else:
#     # Terminate
#         print("Connection unsuccessful")
#         return -1
        
#     c = db.cursor()
#     c.execute("START TRANSACTION;")
#     print(API_Response)

#     SQL = "Insert into btcclosingprice (PK, DATE, USD) values (0,\"2099-7-18 00:00:00\"," + str(API_Response['BTC']['USD'])  + ");"
#     print(SQL)
#     c.execute(SQL)
#     c.execute("COMMIT;")

#     result_ct = c.execute("SELECT * from btcclosingprice;")
#     results = c.fetchall()

#     xy_values = list(results)
#     xy_values = [[item[1].timestamp() , item[2]] for item in xy_values]     # Converting to Unix timestamp for nvD3 x axis format
                
#     # print(xy_values)
#     key = 'BTC USD test'
#     nvd3_JsonFormat = str('{ "key": \"' + key + '\", "values" : ' + str(xy_values) + '})')    
#     with open('test_output.json', 'w') as outfile:
#         outfile.write(nvd3_JsonFormat)

#     return True



import json
def syncDailyPrices(): # Turned off for now needs fine tuning.
    # Connect to the MySQL database
    db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Blockfund')
    # Check if connection was successful
    if (db):
    # Carry out normal procedure
        print("Connection successful")
    else:
    # Terminate
        print("Connection unsuccessful")
        return -1
        
    c = db.cursor()
    c.execute("SELECT Year, MonthOfYear, DayOfMonth FROM DimDate t LEFT JOIN btcclosingprice btc ON t.MYSQL_DateFormat = btc.CALENDAR_DATE WHERE t.MYSQL_DateFormat BETWEEN  '2017-1-1 00:00:00' AND NOW( ) AND btc.USD IS NULL;" )
    missing_dates = list(c.fetchall())
    # c.execute("START TRANSACTION;")
    if len(missing_dates) > 0:
        print("Retrieving and inserting data for dates:")
        print(missing_dates)
        dyn_SQL = "Insert into btcclosingprice (PK, DATE, USD) values "
        for year, month, day in missing_dates:
            print(datetime.datetime(year,month,day))
            historical_price = cryptocompare.get_historical_price('BTC', 'USD', datetime.datetime(year,month,day))  # Get a day in time
            print("BTC on {}-{}-{}: {}".format(year,month,day,historical_price))
            
            dyn_SQL += "(0, '" + str(datetime.datetime(year,month,day)) + "', " + str(float(historical_price['BTC']['USD'])) + "), "
        dyn_SQL = dyn_SQL[:-2] + ";" # Remove the final comma (and space) and add semicolon
        print(dyn_SQL)
        c.execute(dyn_SQL)
        c.execute("COMMIT;")
    else:
        print("BTC USD Up to date.")

    # result_ct = c.execute("SELECT * from btcclosingprice;")
    # results = c.fetchall()
    
    return True




# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=print_date_time,
#     trigger=IntervalTrigger(minutes=1),
#     id='printing_job',
#     name='Print date and time every five seconds',
#     replace_existing=True)
# scheduler.add_job(
#     func=lambda: add_daily_price_to_db('BTC'),      # Must use lambda to pass function referencewith parameters otherwise function fires on app start
#     trigger='cron',
#     year='*', month='*', day="*", week='*', day_of_week='*', hour='*', minute="*", second=5);
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
# ##############################