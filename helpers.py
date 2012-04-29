import pymongo, csv, operator
from datetime import datetime
from pprint import pprint

connection = False
db = False
try:
    connection = pymongo.Connection()
    db = connection.twitpol
except pymongo.errors.AutoReconnect:
    print "ERROR CONNECTING TO DATABASE! Is mongod running?"

def screen_names_in_db():
    """
    Returns a list of all distinct Twitter screen names in the database
    """
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
        print name, db.tweets.find({'words': word, 'author.screen_name': name}).count()

def remove_all_tweets():
    confirm = raw_input("this will remove all tweets from your database, are you sure? (y/n): ")
    if confirm != 'y':
        return
    db.tweets.remove()
    print db.tweets.count(), "total tweets in database"

def print_all_tweets():
    for name in screen_names_in_db():
        for tweet in db.tweets.find({'author.screen_name': name}):
            print name, tweet['text']

def link_frequency():
    for name in screen_names_in_db():
        print "LINK FREQUENCY FOR", name
        link_counts = {}
        for tweet in db.tweets.find({'author.screen_name':name}):
            for url in tweet['entities']['urls']:
                expanded_url = url['expanded_url'].lower()
                if expanded_url in link_counts:
                    link_counts[expanded_url] += 1
                else:
                    link_counts[expanded_url] = 1

        # iterate through link counts dict, sorted by values
        for link_count in sorted(link_counts.iteritems(), key=operator.itemgetter(1), reverse=True):
            if link_count[1] > 1:
                print link_count[1], link_count[0]

def word_frequency():
    boring_words = ['the','to','in','of','and','for','is','on','at','a','be','it','that','with','are','if','its','by']
    for name in screen_names_in_db():
        print "WORD FREQUENCY FOR", name
        word_counts = {}
        for tweet in db.tweets.find({'author.screen_name':name}):
            for word in tweet['words']:
                if word in boring_words: continue
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1

        # iterate through link counts dict, sorted by values
        for word_counts in sorted(word_counts.iteritems(), key=operator.itemgetter(1), reverse=True):
            if word_counts[1] > 10:
                print word_counts[1], word_counts[0]

def export_csv(filename):
    # make a new csv file with name of filename
    new_file = open(filename+'.csv','wb')
    # open the file with csv writer
    csv_file = csv.writer(new_file)
    
    # first row of csv is a list of the keys for all the data columns
    tweet_keys = _recursive_list(db.tweets.find_one(), [], ['words', 'entities'], True)
    entity_types = [['user_mentions','screen_name'], ['hashtags','text'], ['urls','expanded_url']]
    for entity_type in entity_types:
        tweet_keys.append(entity_type[0] + ' count')
        tweet_keys.append(entity_type[0])
    csv_file.writerow([unicode(field).encode('ascii','ignore') for field in tweet_keys])

    for tweet in db.tweets.find().sort('author.screen_name', pymongo.ASCENDING):
        # get basic fields
        tweet_fields = _recursive_list(tweet, [], ['words', 'entities'], False)
        # get limited data about entities
        for entity_type in entity_types:
            # get count for each type of entity
            entities = tweet['entities'][entity_type[0]]
            tweet_fields.append(len(entities))
            # and construct a stringified list of the entities' representative strings
            entity_strings = []
            for entity in entities:
                entity_strings.append(str(entity[entity_type[1]]))
            joined_entities = ', '.join(entity_strings)
            tweet_fields.append(joined_entities)

        csv_file.writerow([unicode(field).encode('ascii','ignore') for field in tweet_fields])

    new_file.close()

def _recursive_list(data, list_so_far, keys_to_ignore, is_key_list):
    if type(data) is dict:
        for key, val in data.iteritems():
            if key in keys_to_ignore:
                continue
            
            if type(val) is dict or type(val) is list:
                _recursive_list(val, list_so_far, keys_to_ignore, is_key_list)
            else:
                item = key if is_key_list else val
                list_so_far.append(item)

    elif type(data) is list:
        list_so_far.append(str(data))

    return list_so_far
