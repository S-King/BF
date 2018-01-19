import MySQLdb, time, logging, csv, datetime

# elapsed_time = time.time() - start_time
# start_time = time.time()


from pymarketcap import Pymarketcap
def LoadCMCHourly():
    coinmarketcap = Pymarketcap()

    # print("Ranks")
    # print(coinmarketcap.ranks())

    try:
        tickers = coinmarketcap.ticker(limit=100)
    except Exception as e:
        # logging.warning("")
        print("CMC API Error: {}".format(e))
        return False    

    csv_filename = "/home/ubuntu/workspace/Blockfund_test/Application/db/CMC_HourlyTicker.csv"
    load_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # So all rows have the same timestamp
    with open(csv_filename, 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for quote in tickers:
            for attribute in quote:
                if quote[attribute] == None:
                    quote[attribute] = 'NULL'
            newrow = [0,quote['id'],quote['name'],quote['symbol'],quote['rank'],quote['price_usd'],
                      quote['price_btc'],quote['24h_volume_usd'],quote['market_cap_usd'],quote['available_supply'],
                      quote['total_supply'],quote['max_supply'],quote['percent_change_1h'],quote['percent_change_24h'],
                      quote['percent_change_7d'],quote['last_updated'], load_timestamp]
            writer.writerow(newrow)
            
    try:
        db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Backload', local_infile = 1)
        # Check if connection was successful
        if (db):
        # Carry out normal procedure 
            pass
            # print("Connection successful")
        else:
        # Terminate
            print("Connection unsuccessful")
            # logging.warning("Database connection error. Symbol: {}, StartDate: {}".format(symbol, snapshot['Data']['General']['StartDate']))
            return -1
        cursor = db.cursor()        
        INSERT_SQL = ("Insert into ODS.CMC_HourlyTicker (PK, id, name, symbol, rank, price_usd, price_btc, volume_usd_24hr, "
                      "market_cap_usd, available_supply, total_supply, max_supply, percent_change_1h, percent_change_24h, "
                      "percent_change_7d, last_updated, Loaddate,) Values ();")
                      
        loadTableSQL = ("LOAD DATA LOCAL INFILE '" + csv_filename + "' INTO TABLE ODS.CMC_HourlyTicker FIELDS OPTIONALLY ENCLOSED BY '\"' "
        "TERMINATED BY ',' LINES TERMINATED BY '\n' (PK,id,name,symbol,rank,price_usd,price_btc,volume_usd_24hr,market_cap_usd, "
        "available_supply,total_supply,max_supply,percent_change_1h,percent_change_24h,percent_change_7d,last_updated,Loaddate);")
        
        cursor.execute("START TRANSACTION;")
        cursor.execute('Truncate table ODS.CMC_HourlyTicker')    # Getting warnings here but the uploads look ok
        cursor.execute(loadTableSQL)    # Getting warnings here but the uploads look ok
        cursor.execute("COMMIT;")     
        print("Tickers Loaded Successfully")
        return True
        
    except Exception as e:
        # logging.warning("")
        print("CMC Insert Error: {}".format(e))
        return False           

def RetrieveCMCRankings():
    time_interval = "1 HOUR"
    try:
        db = MySQLdb.connect(host = '127.0.0.1', user = 'blockroot', passwd = 'pass', db = 'Backload', local_infile = 1)
        # Check if connection was successful
        if (db):
        # Carry out normal procedure 
            pass
            # print("Connection successful")
        else:
        # Terminate
            print("Connection unsuccessful")
            # logging.warning("Database connection error. Symbol: {}, StartDate: {}".format(symbol, snapshot['Data']['General']['StartDate']))
            return -1
    
        LoadRankingSQL = ("Select curr.name, curr.symbol, curr.rank Current_Rank, prev.rank Prev_Rank, curr.rank - prev.rank Rank_Change FROM "
        "(Select * from ODS.CMC_HourlyTicker where loaddate = (Select max(loaddate) from ODS.CMC_HourlyTicker where loaddate <= "
        "DATE_SUB(CURRENT_TIMESTAMP,INTERVAL 1 MINUTE))) prev "
        "inner join " 
        "(Select * from ODS.CMC_HourlyTicker where loaddate = (Select max(loaddate) from ODS.CMC_HourlyTicker)) curr "
        "on prev.symbol  = curr.symbol;")
        
        cursor = db.cursor()    
        result_ct = cursor.execute(LoadRankingSQL)
        results = list(cursor.fetchall())        
    
        print("Tickers Retrieved Successfully")
        print(results)
        return True        
    except Exception as e:
        # logging.warning("")
        print("CMC Retrieve Error: {}".format(e))
        return False           

        
        
# LoadCMCHourly()
    
RetrieveCMCRankings()