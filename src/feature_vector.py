"""
Given a filename for a json file of the processed tweets to be analyzed,
generate the values for the feature vector
"""

import sys
import json
import math

def gen_feature_vector(tweet_dictionary):
    tweet_count = {}
    positive_tweets = {}
    negative_tweets = {}
    net_sentiment = {}
    net_sqr_sentiment = {}
    feature_vector = {}
    max_tweet_count = 0

    for c, tweets in tweet_dictionary.items():
        assert(len(tweets) != 0)
        tweet_count[c] = len(tweets)
        if tweet_count[c] > max_tweet_count:
            max_tweet_count = tweet_count[c]
        positive_tweets[c] = 0
        negative_tweets[c] = 0
        net_sentiment[c] = 0
        net_sqr_sentiment[c] = 0
        feature_vector[c] = {}

        for t in tweets:
            score = float(t['sentiment_score'])
            net_sentiment[c] += score
            # this is score ^ 2 * sign(score)
            net_sqr_sentiment[c] += math.copysign(score ** 2, score)
            if 'sentiment_type' in t and t['sentiment_type'] == 'positive':
                positive_tweets[c] += 1
            elif 'sentiment_type' in t and t['sentiment_type'] == 'negative':
                negative_tweets[c] += 1
        feature_vector[c]['positive_percent'] = positive_tweets[c] / tweet_count[c]
        feature_vector[c]['negative_percent'] = negative_tweets[c] / tweet_count[c]
        feature_vector[c]['average_sentiment'] = net_sentiment[c] / tweet_count[c]
        feature_vector[c]['avg_square_sentiment'] = net_sqr_sentiment[c] / tweet_count[c]
    for c in tweet_dictionary:
        feature_vector[c]['relative_volume'] = tweet_count[c] / max_tweet_count
    return feature_vector


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python feature_vector.py filename')
        exit()
    with open(sys.argv[1], 'r') as tweet_file:
        feature_vector = gen_feature_vector(json.loads(tweet_file.read()))
        for candidate, vector in feature_vector.items():
            print(candidate + ': {')
            for name, value in vector.items():
                print(str.format('{0}:\t {1}', name, value))
            print('}\n\n')
