"""
Quick and dirty script that scrapes tweets out of an html file
"""

import re
import sys

def historical_fetch(in_file, out_file):
    remove_unicode = re.compile('[^\x00-\x7F]')
    cleanr = re.compile('<.*?>')
    remove_data_begin = re.compile('.*data-user-id="')
    remove_data_end = re.compile('".*')
    in_tweet_div = False
    beginning_of_item = True
    found_time = False
    with open(out_file, 'w') as out_file:
        out_file.write('[\n')
        with open(in_file, 'r', encoding='UTF-8') as f:
            for string in f:
                string = re.sub(remove_unicode, ' ', string)
                string = string.replace('\n', '')

                if beginning_of_item:
                    out_file.write('{\n')
                    beginning_of_item = False
                if in_tweet_div:
                    if 'data-tweet-id' in string:
                        user_id = re.sub(remove_data_begin, '', string)
                        user_id = re.sub(remove_data_end, '', user_id)
                        out_file.write('"user": {"id": "%s", "followers_count": 0},\n' % user_id)
                    elif '2015</span>' in string:
                        filtered = re.sub(cleanr, '', string).lstrip()
                        out_file.write('"created_at": "%s",\n' % filtered)
                        found_time = True
                    elif '<p class="TweetTextSize' in string:
                        filtered = re.sub(cleanr, '', string).lstrip()
                        filtered = filtered.replace('"', "'")
                        out_file.write('"text": "%s",\n' % filtered)
                        if not found_time:
                            out_file.write('"created_at": "0",\n')
                        out_file.write('"coordinates": "",\n'
                            + '"favorite_count": 0,\n'
                            + '"retweet_count": 0,\n'
                            + '"entities": { "hashtags": [] }\n'
                            + '},\n\n')
                        in_tweet_div = False
                        beginning_of_item = True
                        found_time = False
                else:
                    if '<div class="tweet original-tweet' in string:
                        in_tweet_div = True
        out_file.write('\n\n]')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python historical_fetch.py in_file out_file')
    else:
        historical_fetch(sys.argv[1], sys.argv[2])
