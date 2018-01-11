import coinmarketcap
import MySQLdb
import json
import csv
import datetime
import time # for timing API calls per second
import logging


    # elapsed_time = time.time() - start_time
    # start_time = time.time()

def syncCMCMarkets():
    caps = coinmarketcap.Market()
    caps.ticker()
    caps.ticker("BTC", limit=3, convert='EUR')
    
# syncCMCMarkets()

from pymarketcap import Pymarketcap
def pymarketcap():
    coinmarketcap = Pymarketcap()

    print("Ranks")
    print(coinmarketcap.ranks())
    
    print("Tickers")
    print(coinmarketcap.ticker(limit=10))
    
pymarketcap()
    
