
import json
import requests
from log import logger
from auth import sess


"""

Twitter returns users and tweets as parsable json.

For this program, I only care about the following attributes:
Tweet: id, text, full_text, user.id

However, the rest are not removed as to be more time efficient

"""

twitter = sess()


def normalize_tweet(tweet):
    """ This defines the API, so to speak, of the tweets """
    if 'full_text' in tweet:
        tweet['text'] = tweet['full_text']
    if 'text' not in tweet:
        tweet['text'] = ''  # iffy, but w.e


def tweets(search):
    """ Get tweets, bruh """
    data = json.loads(twitter.get("https://api.twitter.com/1.1/search/tweets.json",
                                  params={'q': search, 'tweet_mode': 'extended'}).content.decode('utf-8'))

    for tweet in data['statuses']:
        normalize_tweet(tweet)
        yield tweet


def timeline(uid, count):
    """ identif can be user id or user twitter handle (without '@') """
    assert count <= 200

    params = {'count': count, 'tweet_mode': 'extended', 'user_id': uid}
    data = json.loads(
        twitter.get("https://api.twitter.com/1.1/statuses/user_timeline.json", params=params).content.decode('utf-8'))

    for tweet in data:
        if type(tweet) is dict:  # For some reason is sometimes str
            normalize_tweet(tweet)
            yield tweet


def realtime(query):
    while True:
        current = ""
        datastream = twitter.get("https://stream.twitter.com/1.1/statuses/filter.json",
                                 params={'track': query, 'tweet_mode': 'extended'}, stream=True)
        lineiterator = datastream.iter_lines()
        while True:
            try:
                line = next(lineiterator)
            except StopIteration:
                break
            except requests.exceptions.ChunkedEncodingError as e:
                logger.warning(e)

            if not line: continue
            current += line.decode('utf-8')

            try:
                tweet_dict = json.loads(current)  # TODO: Not properly receiving some tweets
            except ValueError:
                pass
            else:
                if not 'text' in tweet_dict: continue  # Happens for some reason idk
                tweet_dict['full_text'] = tweet_dict['text']  # extended mode doesn't seem to be working
                normalize_tweet(tweet_dict)
                yield tweet_dict
                current = ""

