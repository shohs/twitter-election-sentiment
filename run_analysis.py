"""
Convenience script to run tweet analysis on a raw tweet dataset
Runs Partition --> Sentiment --> Predict
"""

import sys
import partition
import sentiment
import predict

def run_analysis(filename, keyword_file, print_all = True):
    partitioned_tweets = partition.partition(filename, keyword_file)
    analyzed_tweets = {}
    for candidate, tweets in partitioned_tweets.items():
        analyzed_tweets[candidate] = sentiment.run_sentiment_analysis(tweets, 'words')
    predict.predict(analyzed_tweets, print_all)


if __name__ == '__main__':
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print('Usage: python run_analysis.py raw_tweet_file, keyword_file [print_all = True]')
    else:
        print_all = True if len(sys.argv) == 3 else (sys.argv[3].lower() == 'true')
        run_analysis(sys.argv[1], sys.argv[2], print_all)
