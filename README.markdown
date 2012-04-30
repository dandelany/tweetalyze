# TwitPolitics
Dan Delany, Michelle Forelle, Sarah Sullivan
## Contents
1. [Introduction](#introduction)
2. [Setup Instructions](#setup-instructions)
    * [Basic Setup](#basic-setup)
    * [Step-by-step Instructions](#step-by-step-instructions)
3. [Helpers Module](#helpers-module)

TwitPolitics is a set of Python scripts for scraping tweets from the Twitter timelines of a set of given usernames. The intent behind their creation was to collect & analyze tweets sent by GOP Presidential candidates during the 2012 GOP primary campaign season, but the code could easily be adapted for other datasets and analyses.

# Setup Instructions
## Basic Setup
The dependencies for TwitPolitics are Python 2.6-2.x, MongoDB (2.0.4), and Python libraries pymongo (2.1.1) and tweepy.

We recommend using Homebrew to install MongoDB and pip to install pymongo and tweepy. Once dependencies are installed, start mongod and run the setup.py script, which will ensure everything is installed correctly by making a test call to the Twitter API, and inserting a tweet in a test collection.

## Step-by-step Instructions
### Installing MongoDB
TwitPolitics uses MongoDB as a database for storing tweets. To install MongoDB, follow the instructions at http://www.mongodb.org/display/DOCS/Quickstart or follow the OS X instructions below.

If you are using Mac OS X, we recommend using Homebrew to install MongoDB. To determine if you have Homebrew installed, type "brew" at the Terminal command line. If not, paste the following on the command line:

    /usr/bin/ruby -e "$(/usr/bin/curl -fksSL https://raw.github.com/mxcl/homebrew/master/Library/Contributions/install_homebrew.rb)"

Once Homebrew is installed, MongoDB can be installed with the following commands:

    brew update
    brew install mongodb
    sudo mkdir -p /data/db/
    sudo chown `id -u` /data/db

Once you have successfully installed MongoDB, open another Terminal tab and type "mongod". This will start an instance of the MongoDB server. mongod will need to be running anytime you are accessing the database, eg. inserting tweets or making queries about them.

### Installing Python Libraries
This project uses two Python libraries, pymongo and tweepy. We recommend using pip to install these libraries. To determine if you have pip installed, type "pip --version" at the command line. If not, you can follow the instructions at http://www.pip-installer.org/en/latest/installing.html or just type the following commands:

    curl -O http://python-distribute.org/distribute_setup.py
    sudo python distribute_setup.py
    curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    sudo python get-pip.py

Type "pip --version" and you should now see the version of pip you are running. The necessary Python libraries can now be installed by typing the commands:

    sudo pip install pymongo
    sudo pip install tweepy

### Running the setup script


# Helpers Module
### export_csv(filename)
    Exports a CSV file containing nearly all known data about all tweets in the database.

    Leaves out a few details about entities.

### link_frequency()
    For each screen name in the database, prints a list of links in tweets, ordered by number of times tweeted.

### print_all_tweets()
    Prints the text of all tweets in the database.

### remove_all_tweets()
    Removes all tweets from the database. Cannot be undone.

### screen_names_in_db()
    Returns a list of all distinct Twitter screen names in the database.

### total_tweets()
    Prints the total number of tweets for each screen name in the database.

### tweets_per_day()
    Prints the average number of tweets per day for each screen name in database.

### tweets_with_word(word)
    Prints the number of tweets containing a given word or list of words for each screen name in database.

### word_frequency()
    For each screen name in the database, counts the frequency of words used and prints them in order of frequency.

    By default, the following frequently occurring words are filtered out of this analysis:
    ['the','to','in','of','and','for','is','on','at','a','be','it','that','this','with','are','if','its','by']