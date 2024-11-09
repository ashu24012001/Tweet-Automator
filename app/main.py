from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime, timedelta
import gspread

service_account = gspread.service_account(filename="credentials.json")
spreadsheet = service_account.open_by_key("1WEjSO6NqKeWiyNbScRqy3MJ4azzXS6StiAOOFMT9DgI")
worksheet = spreadsheet.sheet1

app = Flask(__name__)

class Tweet:
    def __init__(self, time, message, done, row_idx):
        self.time = time
        self.message = message
        self.done = done
        self.row_idx = row_idx

def get_date_time(date_time_str):
    date_time_obj = None
    error_code = None

    try:
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        current_time_ist = datetime.utcnow() + timedelta(hours=5, minutes=30) #converting GMT/UTC to IST
        if not date_time_obj > current_time_ist:
            error_code = "Error! Time must be in future"
    except ValueError as e:
        error_code = f"Error! {e}"

    return date_time_obj, error_code


@app.route('/')
def tweet_list():
    tweet_list = worksheet.get_all_records()
    tweets=[]
    num_open_tweets=0
    for idx, tweet in enumerate(tweet_list, start=2): #start=2 means tweet idx starts from 2
        tweet = Tweet(**tweet, row_idx=idx)
        if not tweet.done:
            num_open_tweets += 1
        tweets.append(tweet)

    tweets.reverse()
    return render_template('base.html', tweets=tweets, num_open_tweets=num_open_tweets)

@app.route('/tweet', methods=['POST'])
def add_tweet():
    message = request.form.get('message')
    if not message:
        return "Error! No message"
    time = request.form.get('time')
    if not time:
        return "Error! No time"
    password = request.form.get('password')
    if not password:
        return "Error! No password"
    if len(message) > 280:
        return "Error! Message too long"
    
    date_time_obj, error_code = get_date_time(time)

    if error_code:
        return error_code
    
    worksheet.append_row([str(date_time_obj), message, 0])
    return redirect(url_for('tweet_list'))

@app.route('/delete/<int:row_idx>')
def delete_tweet(row_idx):
    worksheet.delete_rows(row_idx)
    return redirect(url_for('tweet_list'))

if __name__ == '__main__':
    app.run(debug=True)