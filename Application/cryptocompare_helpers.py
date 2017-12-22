import cryptocompare
import MySQLdb
import json
import csv
import datetime
import time # for timing API calls per second
import logging

# Get the historical price for the supplied currency, supply symbol of currency like ETH-US
    # cryptocompare.get_historical_price('BTC', 'USD', datetime.datetime(2017,11,17))  # Get a day in time
    # cryptocompare.get_price('BTC',curr='USD',full=True)  # Get all current info
# See if the response changes on 11/18+
# >>> cryptocompare.get_historical_price('BTC', 'USD', datetime.datetime(2017,11,17))
# {'BTC': {'USD': 7874.4}}

def loadDashboardChartsJson():
    chartTitle = "line"
    db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Backload')
    # Check if connection was successful
    if (db):
    # Carry out normal procedure 
        print("Connection successful")
    else:
    # Terminate
        print("Connection unsuccessful")
        return -1
        
    c = db.cursor()
    result_ct = c.execute("SELECT * from btcusd_closingprice order by date;") ## Bitcoin Values 
    results = c.fetchall()
    btc_values = [[int(dailyprice[1].strftime("%s")), dailyprice[2]] for dailyprice in results]
    
    # result_ct = c.execute("SELECT * from ethusd_closingprice order by date;") ## Ethereum Values
    # results = c.fetchall()
    # eth_values = [[int(dailyprice[1].strftime("%s")), dailyprice[2]] for dailyprice in results]    
    
    # result_ct = c.execute("SELECT * from ltcusd_closingprice order by date;") ## Litecoin Values
    # results = c.fetchall()
    # ltc_values = [[int(dailyprice[1].strftime("%s")), dailyprice[2]] for dailyprice in results]     
  
    # nvd3_JsonFormat = str('{ "nvd3": {  "' + chartTitle + '": [{ "key": "' + "BTC" + '", "values" : ' + str(btc_values) + '},' +
    # '{ "key": "' + "ETH" + '", "values" : ' + str(eth_values) + '},' +
    # '{ "key": "' + "LTC" + '", "values" : ' + str(ltc_values) + '}]}}')
    
    nvd3_JsonFormat = str('{ "nvd3": {  "' + chartTitle + '": [{ "key": "' + "BTC" + '", "values" : ' + str(btc_values) + '}]}}')





    # Create and output file and write the data to it
    with open('./static/json/chart_test.json', 'w') as outfile:
        outfile.write(nvd3_JsonFormat)    
        outfile.close()


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


# Improvements needed:
# Need to add error checking for API, check that the response key is not "ERROR" like below:
#>>> cryptocompare.get_snapshotbyid(99999)
#{'Type': 4, 'Data': {'SEO': {}, 'ICO': {}, 'StreamerDataRaw': [], 'Subs': [], 'General': {}}, '
# Message': "Yay there is an id, it's numeric so 100% for the effort, but sadly the number is not useful in any way. What are you trying to do?", 'Response': 'Error'}

def fullBackloadBySymbolandCurrency(symbol, currency):
    start_time = time.time()
    coin_list = cryptocompare.get_coin_list(format=False)
    print("Symbol: {}, Id: {}".format(symbol,coin_list[symbol]['Id']))
    snapshot = cryptocompare.get_snapshotbyid(coin_list[symbol]['Id'])
    # Get start date for API from the snapshot list then convert to MYSQL date format
    start_date = datetime.datetime.strptime(snapshot['Data']['General']['StartDate'], '%d/%m/%Y').strftime('%Y-%m-%d') 
    print(snapshot['Data']['General']['StartDate']) # Get ICO date, or whatever they consider a start date #
    if snapshot['Data']['General']['StartDate'] < '01/01/2000':
        print("Invalid date range, skipping")
        logging.warning("Invalid date range for {}, supposed start date: {}".format(symbol, snapshot['Data']['General']['StartDate']))
        return False
    db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Backload', local_infile = 1)
    # Check if connection was successful
    if (db):
    # Carry out normal procedure 
        print("Connection successful")
    else:
    # Terminate
        print("Connection unsuccessful")
        logging.warning("Database connection error. Symbol: {}, StartDate: {}".format(symbol, snapshot['Data']['General']['StartDate']))
        return -1
    cursor = db.cursor()
    #print("SELECT CALENDAR_DATE from DimDate where CALENDAR_DATE >= CAST('{}' AS DATE) AND CALENDAR_DATE < date(now()) order by CALENDAR_DATE limit 10;".format(start_date))
    result_ct = cursor.execute("SELECT CALENDAR_DATE from DimDate where CALENDAR_DATE >= CAST('{}' AS DATE) AND CALENDAR_DATE < date(now()) order by CALENDAR_DATE;".format(start_date))
    results = list(cursor.fetchall())
    print("{} days to load.".format(len(results)))
    row_ct = 0
    if len(results) > 0:   
        if cryptocompare.get_historical_price(symbol, currency, datetime.datetime.combine(results[0][0], datetime.datetime.min.time())) == None:
            with open('allcoins/nodatacurrency.csv', 'a', newline='\n') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow("No data returned for: {} - {}".format(symbol, currency))
            return True
        
        with open("allcoins/" + symbol + currency + '_' + 'loadHistoricalDailyPrices.csv', 'a', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in results:
                row_ct += 1
                time.sleep(0.5) # Slow down the API calls so as to not get banned.
                historical_date = datetime.datetime.combine(row[0], datetime.datetime.min.time()) # Ugggh, did I make this column date instead of datetime? This is a quick fix until I fix the db datatype 
                for attempt in range(5): # Try to reconnect 5 times if we can't connect
                    try:
                        historical_price = cryptocompare.get_historical_price(symbol, currency, historical_date)
                    except:
                        print("Retrying API Call...")
                        historical_price = cryptocompare.get_historical_price(symbol, currency, historical_date)
                    else:
                      break
                else:
                    print("Backloading failed, API calls got denied. Exiting...")
                    return False
                print('{} rows inserted!'.format(row_ct), end='\r')
                
                try:
                    writer.writerow([0,historical_date, historical_price[symbol][currency]])
                except:
                    logging.warning("Writerow error - Symbol: {}, Currency: {}, historicaldate: {}, historical_price: {}".format(symbol, currency, historical_date, historical_price))
                    return False
    else:
        print("{} - {} backload complete.".format(symbol, currency))
    elapsed_time = time.time() - start_time
    print("{}: {} rows inserted in {}s.\nAPI call frequency: {}".format(symbol,row_ct, elapsed_time, float(elapsed_time)/float(row_ct)))
    print("(If call frequency exceeds 1.67 they will ban the IP)")
    
    # Now create the db tables and load them from CSV
    try:
        createTableSQL = "CREATE TABLE {}{}_closingprice (`PK` int(11) NOT NULL AUTO_INCREMENT,`date` datetime DEFAULT NULL,`{}` double DEFAULT NULL, PRIMARY KEY (`PK`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;".format(symbol.lower().replace("*",""),currency.lower(), currency)
        result_ct = cursor.execute(createTableSQL)    

        loadTableSQL = "LOAD DATA LOCAL INFILE '~/workspace/Random/allcoins/{}{}_loadHistoricalDailyPrices.csv' INTO TABLE {}{}_closingprice FIELDS OPTIONALLY ENCLOSED BY '\"' TERMINATED BY ',' LINES TERMINATED BY '\n' (PK,@DATE,USD) SET DATE = STR_TO_DATE(@DATE, '%Y-%m-%d %H:%i:%s');".format(symbol, currency, symbol.lower(), currency.lower())
        cursor.execute("START TRANSACTION;")
        cursor.execute(loadTableSQL)    # Getting warnings here but the uploads look ok
        cursor.execute("COMMIT;")
    except Exception as e:
        print("Create or load table error:\n{}".format(e))
    return True    

        

def syncInstantPrices(cryptolist, currencylist):
    price_list = []
    for crypto in cryptolist:
        for currency in currencylist:
            price = cryptocompare.get_price(crypto,curr=currency)[crypto][currency]
            price_list.append([crypto+currency,price])
            
    # Try to update using one long insert statement, this may not be good for performance
    # Insert the results as one long SQL statement, not ideal for large inserts
    for i in price_list:
        print(i[0])
        dyn_SQL = "Insert into " + i[0].lower() + "_instantprices (PK, DATE, USD) values (0, '" + str(datetime.datetime.now()) + "', " + str(i[1]) + ");"
    print(dyn_SQL)

    # Connect to the MySQL database
    db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Blockfund')
    # Check if connection was successful
    if (not db):
    # Terminate
        print("Connection unsuccessful")
        return -1
    else:
        c = db.cursor()
        c.execute("START TRANSACTION;")
        c.execute(dyn_SQL)
        c.execute("COMMIT;")
        print('Insert Complete')

        return True        
        
        
def syncMarkets(): # Fetch top 25
    print("Beginning marketcap sync")
    orderedCoinList = []
    full_list = cryptocompare.get_coin_list()

    # Get list of all coins
    row_ct = 0
    with open('./MarketCaps.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for symbol in list(full_list):
            row_ct += 1 
            try:
                marketData = cryptocompare.get_price(symbol, 'USD', full=True)['RAW']
                data = [0,symbol,marketData[symbol]['USD']['MKTCAP'], marketData[symbol]['USD']['PRICE'], marketData[symbol]['USD']['VOLUME24HOUR'], marketData[symbol]['USD']['SUPPLY'], marketData[symbol]['USD']['CHANGEPCT24HOUR'], str(datetime.datetime.now())]
                writer.writerow(data)  
                print("{}. Data inserted for {}".format(row_ct, symbol), end='\r')
            except Exception as inst:
                # print(inst)
                pass
            
    # Connect to the MySQL database
    db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Blockfund',  local_infile = 1)
    # Check if connection was successful
    if (not db):
    # Terminate
        print("Connection unsuccessful")
        return -1
    else:
        try:
            cursor = db.cursor()           
            loadTableSQL = "LOAD DATA LOCAL INFILE '~/workspace/Blockfund_test/Application/db/MarketCaps.csv' INTO TABLE marketcaps FIELDS OPTIONALLY ENCLOSED BY '\"' TERMINATED BY ',' LINES TERMINATED BY '\n' (PK,symbol, marketcap, price, volume24hr, supply, percentchange24hr, @date) SET DATE = STR_TO_DATE(@DATE, '%Y-%m-%d %H:%i:%s');"
            cursor.execute("START TRANSACTION;")
            cursor.execute("Truncate table marketcaps;")
            cursor.execute(loadTableSQL)    # Getting warnings here but the uploads look ok
            cursor.execute("COMMIT;")
        except Exception as e:
            print("Error loading marketcaps: {}".format(e))
    print("Marketcaps loaded")

    return True        