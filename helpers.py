import pymongo, csv
from datetime import datetime

connection = pymongo.Connection()
db = connection.twitpol

def screen_names_in_db():
    return db.tweets.distinct('author.screen_name')

def total_tweets():
    # prints the total number of tweets for each screen name in the database
    print 'total tweets:', db.tweets.count()
    for name in screen_names_in_db():
        print name, db.tweets.find({'author.screen_name':name}).count()

def tweets_per_day():
    # prints the average number of tweets per day for each screen name in database
    for name in screen_names_in_db():
        first_date = db.tweets.find({'author.screen_name':name}).sort('created_at', pymongo.ASCENDING)[0]['created_at']
        diff_days = (datetime.now() - first_date).days
        total = db.tweets.find({'author.screen_name':name}).count()
        avg = float(total) / float(diff_days)
        print name, avg, "tweets per day since", first_date

def tweets_with_word(word):
    # prints the number of tweets containing a given word for each screen name in database
    for name in screen_names_in_db():
        print name, db.tweets.find({'words':word,'author.screen_name':name}).count()

def remove_all_tweets():
    confirm = raw_input("this will remove all tweets from your database, are you sure? (y/n): ")
    if confirm != 'y':
        return
    db.tweets.remove()
    print db.tweets.count(), "total tweets in database"

def print_all_tweets():
    for name in screen_names_in_db():
        for tweet in db.tweets.find({'author.screen_name':name}):
            print name, tweet['text']

def export_csv(filename):
    # make a new csv file with name of filename
    new_file = open(filename+'.csv','wb')
    new_file.close()
    # open the file with csv writer
    csv_file = csv.writer(open(filename+'.csv', 'wb'))
    
    for tweet in db.tweets.find():
        csv_file.writerow([tweet['author']['screen_name'], tweet['text'].encode('ascii', 'replace')])
    