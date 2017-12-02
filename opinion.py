
import json
import twitter
from misc import Avg
from collections import defaultdict

with open('words.json') as wordsf:
    words = json.load(wordsf)
positive = set(words['positive'])
negative = set(words['negative'])

def removeChars(string, chars):
    ret = ""
    for c in string:
        if c not in chars:
            ret += c
    return ret

def get_words(sentence):
    sentence = removeChars(sentence, "\"'~!@#$%^&*()`1234567890-_=+<>,.?/;:\\|[]{}")
    return sentence.lower().split(' ')

def opinion(words):
    op = 0
    for word in words:
        if word in positive: op += 1
        elif word in negative: op += 1
    return float(op) / len(words)


def profile(user: twitter.User):
    """ Profile a user's opinion.
    Iterates through 200 recent user tweets and
    catalogues the user's opinion of all (significant (todo))
    words said in the timeline. """
    tweets = twitter.timeline(user, 200)

    opinions = defaultdict(lambda: Avg())
    for tweet in tweets:
        words = get_words(tweet.text)
        op = opinon(words)
        for word in words:
            opinions[word].add(op)

    return opinions





