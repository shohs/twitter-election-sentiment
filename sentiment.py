"""
Given a list of tweets, run sentiment analysis on the selected field
"""
import copy
import json
import sys
from alchemyapi import AlchemyAPI

def run_sentiment_analysis(tweets, text_key):
    def print_error(response):
        # This should be replaced with better logging
        print('Error with AlchemyAPI response:')
        print(sentiment, '\n')

    alchemyapi = AlchemyAPI()
    results = []
    for item in tweets:
        if text_key not in item:
            # Assume it's a bad tweet and continue
            print(text_key, 'not found in tweet')
            continue
        sentiment = alchemyapi.sentiment('text', item['words'])
        try:
            if sentiment['status'].lower() == 'error':
                # Unrecognized language, emoji only, etc...
                print_error(sentiment)
            # Make a deep copy (since it's a nested dictionary)
            new_item = copy.deepcopy(item)
            sentiment_type = sentiment['docSentiment']['type']
            new_item['sentiment_type'] = sentiment_type
            if sentiment_type == 'neutral':
                new_item['sentiment_score'] = 0
            else:
                new_item['sentiment_score'] = sentiment['docSentiment']['score']
            results.append(new_item)
        except Exception as ex:
            print(type(ex).__name__)
            print_error(sentiment)

    return results

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python sentiment.py tweet_file, text_key')
    else:
        with open(sys.argv[1]) as tweet_file:
            tweets = json.loads(tweet_file.read())
            sentiment_tweets = run_sentiment_analysis(tweets, sys.argv[2])
            for tweet in sentiment_tweets:
                print(tweet, '\n')
