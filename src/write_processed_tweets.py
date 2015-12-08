"""
Process and write the tweets to a file so the sentiment analysis doesn't need to be
run multiple times. Runs partition and sentiment, then writes the results to a file
"""

import sys
import json
import partition
import sentiment

def write_processed_tweets(raw_tweet_file, keyword_file, output_file):
    partitioned_tweets = partition.partition(raw_tweet_file, keyword_file)
    sentiment_tweets = {}
    for candidate, tweets in partitioned_tweets.items():
        sentiment_tweets[candidate] = sentiment.run_sentiment_analysis(tweets, 'words')

    with open(output_file, 'w') as data_file:
        data_file.write('{\n')
        first_candidate = True
        for candidate, tweets in sentiment_tweets.items():
            if first_candidate:
                first_candidate = False
            else:
                data_file.write(',\n')
            data_file.write('"' + candidate + '": [\n')
            first_item = True
            for tweet in tweets:
                if first_item:
                    first_item = False
                else:
                    data_file.write(',\n')
                data_file.write(json.dumps(tweet))
            data_file.write(']\n')
        data_file.write('}')

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python write_processed_tweets.py raw_tweet_file, keyword_file, output_file')
    else:
        write_processed_tweets(sys.argv[1], sys.argv[2], sys.argv[3])
