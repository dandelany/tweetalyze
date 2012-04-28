# import all the libraries we're using
import time, pprint, re
from datetime import datetime
import pymongo, tweepy

# a function for replacing unicode characters with ascii
def ascii_encode(text):
    text = text.replace(u'\u2019',u'\'').replace(u'\u0160',u'')
    text = text.replace(u'\u8211',u'-').replace(u'\u8220',u'"').replace(u'\u8221',u'"')
    text = text.replace(u'\u201c',u'"').replace(u'\u201d',u'"')
    text.encode('ascii','ignore')
    return text

try:
    # connect to Mongo database
    connection = pymongo.Connection()
    db = connection.twitpol
    print "ready to scrape some tweets!"

    # ask the user for a date
    date_string = raw_input("input starting date in mm/dd/yyyy format: ");
    date_list = date_string.split('/')
    start_date = datetime(int(date_list[2]), int(date_list[0]), int(date_list[1]))
    print "start date:", start_date

    # ask user to confirm the date is correct
    confirm = raw_input("that's " + str((datetime.now() - start_date).days) + " days of tweets, are you sure? (y/n): ")
    if confirm != 'y':
        exit()

    # a list of usernames to get twitter updates from
    usernames = ['mittromney','jonhuntsman','governorperry','newtgingrich','ronpaul','ricksantorum','buddyroemer']
    # go through each of the names...
    for name in usernames:
        print "GETTING TWEETS FOR", name
        is_done = False
        page = 1
        # and use tweepy to get last 200 tweets from the name's timeline
        while not is_done:
            print "GETTING", name, "PAGE", page
            try:
                tweets = tweepy.api.user_timeline(screen_name=name, count=200, include_rts=1, include_entities=1, page=page)
            except tweepy.error.TweepError:
                print "TWEEPY ERROR... retrying in 30 seconds"
                time.sleep(30)
                tweets = tweepy.api.user_timeline(screen_name=name, count=200, include_rts=1, include_entities=1, page=page)

            # go through each of their tweets...
            for tweet in tweets:
                # see if tweet date falls before start date...
                start_date_diff = tweet.created_at - start_date
                if start_date_diff.days < 0: 
                    # if so, we're done, so break out of loop
                    is_done = True
                    break
                print "tweet date:", tweet.created_at, ",", start_date_diff.days, "days after start date"
                print tweet.author.screen_name, ': "', tweet.text, '"'

                # make a tweet object with all the info we want to save about tweet
                tweet_text = ascii_encode(tweet.text)
                
                tweet_object = {
                    '_id': tweet.id_str,
                    
                    'author': {
                        'name': tweet.author.name,
                        'screen_name': tweet.author.screen_name.lower(),
                        'followers_count': tweet.author.followers_count,
                        'friends_count': tweet.author.friends_count
                    },
                    'text': tweet_text,
                    'words': re.sub('[^a-zA-Z0-9_\-@# ]', '', tweet_text).lower().split(),
                    'created_at': tweet.created_at,
                    
                    'retweet_count': tweet.retweet_count,
                    'truncated': tweet.truncated,
                    'favorited': tweet.favorited,
                    
                    'entities': tweet.entities
                }
                
                # get retweet status if it exists
                try:
                    retweeted_status = tweet.retweeted_status
                    tweet_object['is_retweet'] = True
                    tweet_object['retweeted_from'] = retweeted_status.author.screen_name
                except AttributeError:
                    tweet_object['is_retweet'] = False
                    tweet_object['retweeted_from'] = False
                
                #print tweet.text
                # insert the object in a database collection called tweets
                db.tweets.insert(tweet_object)

            if not is_done:
                # wait for 25 seconds to avoid hitting Twitter API rate limit
                print "not done yet... need another page"
                page = page + 1
                print db.tweets.find({'author.screen_name': name}).count(), "total", name, "tweets in database"
                print "waiting 30 seconds until next request..."
                time.sleep(30)

        print "got all tweets for", name, "since", start_date
        print db.tweets.find({'author.screen_name': name}).count(), "total", name, "tweets in database"
        # if this wasn't the last username, wait for 30 secs before requesting next username
        if name != usernames[-1]:
            print "waiting 30 seconds until next request..."
            time.sleep(30)
    
    # count the number of tweets in database and print it
    tweet_count = db.tweets.count()
    print "TWEETS COLLECTION IN DATABASE CONTAINS", tweet_count, "TWEETS"

except pymongo.errors.AutoReconnect:
    print "ERROR CONNECTING TO DATABASE! Is mongod running?"