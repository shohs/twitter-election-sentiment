"""
Collect a set of tweets based on keywords and save them to a specified file
"""

import sys
import tweepy
import json
import signal

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

consumer_key = 'pz8APe0EtRV5lOMYlFO3aYcqg'
consumer_secret = '9k7iYL513ehCss9OzrBftdEtwA52ejbWwuLdUjWcq9SzBFYvJC'
access_token = '598819937-oT83AwuIaz3MKmHh4rsVTHVlybB1RV1t2Uuci5n8'
access_token_secret = 'w2povbjUR5ku1GJenHRgxnaFLYXaexuxkijjjeLkPr8sR'

# This is global so it can be access in the ctrl-c interrupt
tweet_writer = None

class TweetStreamWriter:
    def __init__(self, output_file):
        self.data = []
        self.output_file = output_file

    def add_tweet(self, tweet_data):
        self.data.append(tweet_data)

    def store_twitter_data(self):
        with open(self.output_file, 'w') as data_file:
            first_item = True
            data_file.write('[')

            for item in self.data:
                if first_item:
                    first_item = False
                else:
                    data_file.write(',')
                data_file.write(item)

            data_file.write(']')

        self.data = []

    def cleanup(self):
        # Write the extra data if there is any
        if self.data:
            self.store_twitter_data()


class TwitterStreamReader(StreamListener):
    def __init__(self, tweet_aggregator, max_tweets):
        self.tweet_aggregator = tweet_aggregator
        self.count = 0
        self.max_tweets = max_tweets

    def on_data(self, data):
        self.tweet_aggregator.add_tweet(data)
        self.count += 1
        return (self.count < self.max_tweets)

    def on_error(self, status):
        print(status)


def collect_tweets(output_file, max_tweets, keywords):
    def signal_handler(signal, frame):
        global tweet_writer
        tweet_writer.cleanup()
        sys.exit(0)

    # Register a signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    global tweet_writer
    tweet_writer = TweetStreamWriter(output_file)
    stream_reader = TwitterStreamReader(tweet_writer, max_tweets)

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, stream_reader)
    stream.filter(track=keywords)
    tweet_writer.cleanup()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python stream.py output_file max_tweets keywords...')
        exit()
    collect_tweets(sys.argv[1], int(sys.argv[2]), sys.argv[3:])
