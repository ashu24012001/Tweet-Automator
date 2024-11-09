import gspread
from dotenv import load_dotenv #load_dotenv loads data from .env file
from os import environ #environ is used to get hold of keys from .env file
import tweepy #twitter API python library
from datetime import datetime, timedelta
import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

CONSUMER_KEY = environ['consumer_key']
CONSUMER_SECRET = environ['consumer_secret']
ACCESS_TOKEN = environ['access_token']
ACCESS_TOKEN_SECRET = environ['access_token_secret']
BEARER_TOKEN = environ['bearer_token']

INTERVAL = int(environ['interval'])
DEBUG = environ['debug'] == 1  

client = tweepy.Client(bearer_token=BEARER_TOKEN, 
                       consumer_key=CONSUMER_KEY, 
                       consumer_secret=CONSUMER_SECRET, 
                       access_token=ACCESS_TOKEN, 
                       access_token_secret=ACCESS_TOKEN_SECRET)

# api = tweepy.API(auth)
service_account = gspread.service_account(filename="credentials.json")
spreadsheet = service_account.open_by_key("1WEjSO6NqKeWiyNbScRqy3MJ4azzXS6StiAOOFMT9DgI")
worksheet = spreadsheet.sheet1

def main():
    while True:
        tweet_list = worksheet.get_all_records()
        current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        logger.info(f"{len(tweet_list)} tweets found at {current_time.time()}")

        for idx, tweet in enumerate(tweet_list, start=2):
            message = tweet['message']
            tweet_time = tweet['time']
            done = tweet['done']

            date_time_obj = datetime.strptime(tweet_time, '%Y-%m-%d %H:%M:%S')

            if not done:
                if date_time_obj <= current_time:
                    logger.info("This should be tweeted")

                    try:
                        client.create_tweet(text=message)
                        worksheet.update_cell(idx, 3, 1)
                    except Exception as e:
                        logger.warning(f"Error occured during tweet posting! {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
