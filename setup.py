# import all the libraries we're using
# pymongo, for accessing database
import pymongo
print ">>> pymongo installed successfully..."
# tweepy, for accessing twitter API
import tweepy
print ">>> tweepy installed successfully..."
# other helpers
import time, datetime, re
from pprint import pprint

# 'try' allows us to catch errors if they happen, and print an appropriate error message
try:
    # connect to Mongo database
    connection = pymongo.Connection()
    db = connection.twitpol_test
    print ">>> connected to database successfully..."

    # try to get a tweet from the twitter API
    print ">>> connecting to twitter API..."

    tweets = tweepy.api.user_timeline(screen_name='barackobama', count=1, include_rts=1, page=1)

    print ">>> got one of barackobama's tweets!"
    print tweets
    # grab the first one in the list
    tweet = tweets[0]
    print ">>> data in tweet:"
    # pprint and __dict__ just help us print the tweet nicely... this is basically just "print tweet"
    pprint(tweet.__dict__)
    print ">>> data in tweet.author:"
    pprint(tweet.author.__dict__)

    # make a tweet object with all the info we want to save about tweet
    tweet_object = {
        'author': {
            'name': tweet.author.name,
            'screen_name': tweet.author.screen_name
        },
        'text': tweet.text,
        'words': re.sub('[^a-zA-Z0-9_\-@# ]', '', tweet.text).lower().split(),
        'created_at': tweet.created_at,
        '_id': tweet.id_str
    }
    print ">>> data we've selected from tweet and tweet.author to save in database:"
    pprint(tweet_object)

    try:
        # insert the object in a database collection called tweets
        db.tweets.insert(tweet_object)
        print ">>> successfully added tweet to database!"
    except:
        print ">>> ERROR ADDING TWEET TO DATABASE!"
    
    # print the total number of tweets in database
    print ">>>", db.tweets.count(), "tweet(s) in database."

except pymongo.errors.AutoReconnect:
    print ">>> ERROR CONNECTING TO DATABASE! Is mongod running?"

