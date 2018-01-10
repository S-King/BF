import feedparser
import csv
import datetime
import MySQLdb

def syncNews():
    rss_feeds = ["https://cryptocurrencynews.com/feed/", "https://www.tradingview.com/feed/?stream=bitcoin"]
    with open('./NewsFeed.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for feed in rss_feeds:
            full_feed = feedparser.parse(feed)
            for article in full_feed.entries:
                # print(article)
                data = [0, str(article['title']), str(article['link']), datetime.datetime.strptime(article['published'], "%a, %d %b %Y %H:%M:%S %z"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                writer.writerow(data)  


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
            loadTableSQL = "LOAD DATA LOCAL INFILE '~/workspace/Blockfund_test/Application/NewsFeed.csv' INTO TABLE NewsFeed FIELDS ENCLOSED BY '\"' TERMINATED BY ',' ESCAPED BY '~' LINES TERMINATED BY '\r\n' (PK, Title, URL, Published, LastModified);"
            cursor.execute("START TRANSACTION;")
            cursor.execute("Truncate table NewsFeed;")
            cursor.execute(loadTableSQL)    # Getting warnings here but the uploads look ok
            cursor.execute("COMMIT;")
        except Exception as e:
            print("Error loading news: {}".format(e))
    print("NewsFeed loaded")



    
# syncNews()