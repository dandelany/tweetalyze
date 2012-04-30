import pymongo, csv, operator
from datetime import datetime
from pprint import pprint

from helper_decorators import export_csv, print_table, should_return

connection = False
db = False
try:
    connection = pymongo.Connection()
    db = connection.twitpol
except pymongo.errors.AutoReconnect:
    print "ERROR CONNECTING TO DATABASE! Is mongod running?"

@should_return
@export_csv
@print_table
def screen_names_in_db(print_table=False, export_csv=False, should_return=True):
    """
    Returns a list of all distinct Twitter screen names in the database.
    """
    return db.tweets.distinct('author.screen_name')

@should_return
@export_csv
@print_table
def total_tweets(print_table=True, export_csv=False, should_return=False):
    """
    Prints the total number of tweets for each screen name in the database.
    """
    export_data = [['name', '# of tweets']]

    for name in screen_names_in_db():
        export_data.append([name, db.tweets.find({'author.screen_name':name}).count()])

    export_data.append(['TOTAL', db.tweets.count()])
    return export_data

@should_return
@export_csv
@print_table
def tweets_per_day(print_table=True, export_csv=False, should_return=False):
    """
    Prints the average number of tweets per day for each screen name in database.
    """
    export_data = [['screen name', 'average # tweets per day']]

    for name in screen_names_in_db():
        first_date = db.tweets.find({'author.screen_name':name}).sort('created_at', pymongo.ASCENDING)[0]['created_at']
        diff_days = (datetime.now() - first_date).days
        total = db.tweets.find({'author.screen_name':name}).count()
        avg = float(total) / float(diff_days)
        export_data.append([name, avg])

    return export_data

@should_return
@export_csv
@print_table
def tweets_with_word(words, print_table=True, export_csv=False, should_return=False):
    """
    Prints the number of tweets containing a given word or list of words for each screen name in database.
    """
    if type(words) is str: words = [words]
    words_string = " OR ".join(words)
    export_data = [['screen name', '# of tweets containing ' + words_string]]

    for name in screen_names_in_db():
        tweet_count = db.tweets.find({'words': {'$in': words}, 'author.screen_name': name}).count()
        export_data.append([name, tweet_count])

    return export_data

@should_return
@export_csv
@print_table
def entity_frequency(entity_type, min_count=1, print_table=True, export_csv=False, should_return=False):
    """
    For each screen name in the database, counts the frequencies of the most commonly tweeted entities by a particular user.

    eg. helpers.entity_frequency('urls')
    returns the most commonly tweeted urls for each screen name, sorted by frequency of use.
    Valid entity types are 'user_mentions', 'hashtags', and 'urls'.
    """
    entity_fields = {'user_mentions': 'screen_name', 'hashtags': 'text', 'urls': 'expanded_url'}
    if entity_type not in entity_fields:
        print "ERROR: Invalid entity type. Valid types are 'user_mentions', 'hashtags', and 'urls'"

    export_data = [['screen name', entity_type[:-1], '# of mentions']]

    for name in screen_names_in_db():
        entity_counts = {}
        for tweet in db.tweets.find({'author.screen_name':name}):
            for entity in tweet['entities'][entity_type]:
                entity_string = entity[entity_fields[entity_type]].lower()
                if entity_string in entity_counts:
                    entity_counts[entity_string] += 1
                else:
                    entity_counts[entity_string] = 1

        # iterate through link counts dict, sorted by values
        for entity_count in sorted(entity_counts.iteritems(), key=operator.itemgetter(1), reverse=True):
            if entity_count[1] >= min_count:
                export_data.append([name, entity_count[0], entity_count[1]])

    return export_data

@should_return
@export_csv
@print_table
def word_frequency(min_count=10, print_table=True, export_csv=False, should_return=False):
    """
    For each screen name in the database, counts the frequency of words used and prints them in order of frequency.

    By default, the following frequently occurring words are filtered out of this analysis:
    ['the','to','in','of','and','for','is','on','at','a','be','it','that','this','with','are','if','its','by']
    """
    filtered_words = ['the','to','in','of','and','for','is','on','at','a','be','it','that','this','with','are','if','its','by']
    export_data = [['screen name', 'word', '# of times used', 'occurrence per tweet']]

    for name in screen_names_in_db():
        word_counts = {}
        total_tweets = db.tweets.find({'author.screen_name':name}).count()
        for tweet in db.tweets.find({'author.screen_name':name}):
            for word in tweet['words']:
                if word in filtered_words: continue
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1

        # iterate through link counts dict, sorted by values
        for word_counts in sorted(word_counts.iteritems(), key=operator.itemgetter(1), reverse=True):
            if word_counts[1] >= min_count:
                export_data.append([name, word_counts[0], word_counts[1], (float(word_counts[1]) / float(total_tweets))])

    return export_data

def remove_all_tweets():
    """
    Removes all tweets from the database. Cannot be undone.
    """
    confirm = raw_input("this will remove all tweets from your database, are you sure? (y/n): ")
    if confirm != 'y':
        return
    db.tweets.remove()
    print db.tweets.count(), "total tweets in database"

def print_all_tweets():
    """
    Prints the text of all tweets in the database.
    """
    for name in screen_names_in_db():
        for tweet in db.tweets.find({'author.screen_name': name}):
            print name, tweet['text']

def all_tweet_data(filename):
    """
    Exports a CSV file containing nearly all known data about all tweets in the database.

    Leaves out a few details about entities.
    """
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

