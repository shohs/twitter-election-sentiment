"""
Given a list of partitioned and sentiment-analyzed tweets, run several trials
to guess who won the election
"""

import json
import math
import sys
import pprint

import feature_vector

def positive_volume(f):
    return f['relative_volume'] * f['positive_percent']

def inv_negative_volume(f):
    return 1.0 - f['relative_volume'] * f['negative_percent']

def normalized_sentiment(f):
    return (f['average_sentiment'] + 1) / 2

def normalized_square_sentiment(f):
    return (f['avg_square_sentiment'] + 1) / 2

def weighted_sentiment(f):
    return (f['relative_volume'] * f['average_sentiment'] + 1) / 2

# We want a function that's close to 1 unless the relative tweet volume is low
def quadratic_diff_penalty(f, scale):
    val = f['relative_volume']
    return 1 - scale * (1 - val) ** 2

# Experiment using x ** 3 as the penalty function
def cubic_diff_penalty(f, scale):
    val = f['relative_volume']
    return 1 - scale * (1 - val) ** 3


def linear_combination(f, a1, a2, a3, a4 = 0, a5 = 0):
    return (a1 * positive_volume(f)
        + a2 * inv_negative_volume(f)
        + a3 * normalized_sentiment(f)
        + a4 * normalized_square_sentiment(f)
        + a5 * weighted_sentiment(f))

def run_trial(function, feature_map):
    candidate_scores = {}
    total_score = 0
    for candidate, features in feature_map.items():
        score = function(features)
        candidate_scores[candidate] = score
        total_score += score
    for candidate, score in candidate_scores.items():
        candidate_scores[candidate] = score / total_score
    return candidate_scores

def predict(tweet_dictionary, print_all):
    features = feature_vector.gen_feature_vector(tweet_dictionary)
    trial_list = [
        #1
        lambda f: linear_combination(f, 1, 0, 0),
        lambda f: linear_combination(f, 0.5, 0, 0.5),
        lambda f: linear_combination(f, 0.33, 0.33, 0.33),
        lambda f: linear_combination(f, 0.25, 0.25, 0.5),
        lambda f: linear_combination(f, 0.5, 0.25, 0.25),
        lambda f: linear_combination(f, 0.2, 0.1, 0.0, 0.7),
        lambda f: linear_combination(f, 0.0, 0.0, 0.0, 1.0),
        lambda f: linear_combination(f, 0.5, 0.0, 0.0, 0.5),
        lambda f: linear_combination(f, 0.3, 0.15, 0.15, 0.3),
        lambda f: linear_combination(f, 0.5, 0.1, 0.1, 0.3),
        #11
        lambda f: linear_combination(f, 0.6, 0.0, 0.0, 0.4),
        lambda f: linear_combination(f, 0.55, 0.0, 0.2, 0.25),
        lambda f: linear_combination(f, 0.5, 0.1, 0.15, 0.25),
        lambda f: linear_combination(f, 0.5, 0.05, 0.1, 0.35),
        lambda f: linear_combination(f, 0.4, 0.05, 0.1, 0.35, 0.1),
        lambda f: linear_combination(f, 0.45, 0.05, 0.05, 0.35, 0.1),
        lambda f: linear_combination(f, 0.35, 0.0, 0.1, 0.35, 0.2),
        lambda f: linear_combination(f, 0.35, 0.0, 0.1, 0.25, 0.3),
        lambda f: linear_combination(f, 0.35, 0.0, 0.1, 0.25, 0.3) * quadratic_diff_penalty(f, 1),
        lambda f: linear_combination(f, 0.35, 0.0, 0.1, 0.25, 0.3) * quadratic_diff_penalty(f, 0.25),
        # 21
        lambda f: linear_combination(f, 0.25, 0.0, 0.15, 0.4, 0.2) * quadratic_diff_penalty(f, 0.25),
        lambda f: linear_combination(f, 0.25, 0.0, 0.2, 0.45, 0.1) * quadratic_diff_penalty(f, 0.3),
        lambda f: linear_combination(f, 0.25, 0.0, 0.2, 0.45, 0.1) * quadratic_diff_penalty(f, 0.4),
        lambda f: linear_combination(f, 0.2, 0.0, 0.2, 0.5, 0.1) * quadratic_diff_penalty(f, 0.4),
        lambda f: linear_combination(f, 0.2, 0.0, 0.2, 0.5, 0.1) * quadratic_diff_penalty(f, 0.45),
        lambda f: linear_combination(f, 0.15, 0.0, 0.25, 0.55, 0.05) * quadratic_diff_penalty(f, 0.45),
        lambda f: linear_combination(f, 0.15, 0.0, 0.25, 0.55, 0.05) * quadratic_diff_penalty(f, 0.5),
        lambda f: linear_combination(f, 0.15, 0.0, 0.25, 0.55, 0.05) * cubic_diff_penalty(f, 0.5),
        lambda f: linear_combination(f, 0.15, 0.0, 0.25, 0.55, 0.05) * cubic_diff_penalty(f, 0.6),
        lambda f: linear_combination(f, 0.15, 0.0, 0.25, 0.55, 0.05) * cubic_diff_penalty(f, 0.7),
        # 31
        lambda f: linear_combination(f, 0.1, 0.0, 0.25, 0.65, 0) * cubic_diff_penalty(f, 0.7),
        lambda f: linear_combination(f, 0.1, 0.0, 0.25, 0.65, 0) * cubic_diff_penalty(f, 0.75),
        lambda f: linear_combination(f, 0.05, 0.0, 0.25, 0.7, 0) * cubic_diff_penalty(f, 0.75),
    ]

    if print_all:
        print('Feature vector:')
        pprint.pprint(features)
        print('\nTrial Results:')
        for index, function in enumerate(trial_list):
            print('trial %d:' % (index + 1))
            print(run_trial(function, features))
            print()
        print()
    final_trial_result = run_trial(trial_list[-1], features)
    print('Predicted Outcome:')
    max_percent = 0
    winning_candidate = ''
    for candidate, percent in final_trial_result.items():
        print(candidate + ': ', int(percent * 100008) / 1000)
        if (percent > max_percent):
            max_percent = percent
            winning_candidate = candidate
    print('\nProjected Winner:')
    print(winning_candidate)


if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print('Usage: python predict.py filename [print_all = True]')
        exit()
    with open(sys.argv[1], 'r') as tweet_file:
        print_all = True if len(sys.argv) == 2 else (sys.argv[2].lower() == 'true')
        predict(json.loads(tweet_file.read()), print_all)
