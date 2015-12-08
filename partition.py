"""
Given a tweet file and another file containing keywords per candidate,
determine which candidate each tweet refers to and split based on that metric.
Also, retweets are grouped together
"""

import json
import re
import sys
from alchemyapi import AlchemyAPI

def _contains_keywords(tweet, keywords):
    for keyword in keywords:
        if keyword in tweet['words'].lower():
            return True
    return False

def _get_candidates(tweet, candidates):
    matches = []
    for candidate, keywords in candidates.items():
        if _contains_keywords(tweet, keywords):
            matches.append(candidate)
    return matches

"""
Loads the keywords, which should be in the format of a dictionary with the keys
being the candidates' names and the values being a list of filter keywords
"""
def _load_keywords(keyword_filename):
    with open(keyword_filename) as keyword_file:
        return json.loads(keyword_file.read())

def partition(src_filename, keyword_filename):
    # Store the tweets in a dictionary with the text as the key so duplicates can be grouped together
    tweet_dictionary = {}
    with open(src_filename, 'r') as tweet_file:
        json_tweets = json.loads(tweet_file.read())
    for item in json_tweets:
        tweet_text = item['text']
        # Remove the beginning of retweets
        tweet_text = re.sub('^RT @\w+: ', '', tweet_text)
        if tweet_text in tweet_dictionary:
            tweet_dictionary[tweet_text]['ids'].append(item['user']['id'])
        else:
            tweet_data = {}
            tweet_data['location'] = item['coordinates']
            tweet_data['time'] = item['created_at']
            tweet_data['favorites'] = item['favorite_count']
            tweet_data['retweets'] = item['retweet_count']
            tweet_data['followers'] = item['user']['followers_count']
            tweet_data['words'] = tweet_text
            tweet_data['hashtags'] = []
            raw_hashtags = item['entities']['hashtags']
            for hashtag in raw_hashtags:
                tweet_data['hashtags'].append(hashtag['text'])
            tweet_data['ids'] = [item['user']['id']]

            # Handle the case that sentiment analysis has already been run
            if 'sentiment_score' in item:
                tweet_data['sentiment_score'] = item['sentiment_score']
            if 'sentiment_type' in item:
                tweet_data['sentiment_type'] = item['sentiment_type']

            tweet_dictionary[tweet_text] = tweet_data

    keywords = _load_keywords(keyword_filename)

    partitioned_tweets = {}
    for candidate in keywords:
        partitioned_tweets[candidate] = []

    for tweet in tweet_dictionary.values():
        candidates = _get_candidates(tweet, keywords)
        if len(candidates) == 1:
            partitioned_tweets[candidates[0]].append(tweet)
    return partitioned_tweets


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python partition.py filename keyword_file')
    else:
        p = partition(sys.argv[1], sys.argv[2])
        for candidate, tweets in p.items():
            print(p, ': [')
            for tweet in tweets:
                print(json.dumps(tweet), '\n')
            print(']\n\n')
