
import json
import twitter
from misc import Avg
from collections import defaultdict

with open('words.json') as wordsf:
    words = json.load(wordsf)
positive = set(words['positive'])
negative = set(words['negative'])
nouns = set(words['noun'])

def removeChars(string, chars):
    ret = ""
    for c in string:
        if c not in chars:
            ret += c
    return ret

def get_words(sentence):
    sentence = sentence.replace('\n', ' ')
    sentence = removeChars(sentence, "\"'~!@#$%^&*()`1234567890-_=+<>,.?/;:\\|[]{}")
    sentence = sentence.lower().split(' ')
    sentence = filter(lambda v: v != '', sentence)
    return list(sentence)

def opinion(words):
    if type(words) is not list:
        raise ValueError("You're probably calling opinon(string). Call opinion(get_words(string))")
    if not words: return 0
    op = 0
    for word in words:
        if word in positive: op += 1
        elif word in negative: op -= 1
    return float(op) / len(words)


def profile(user):  # user: twitter.User
    """ Profile a user's opinion.
    Iterates through 200 recent user tweets and
    catalogues the user's opinion of all (significant (todo))
    words said in the timeline. """
    tweets = twitter.timeline(user, 200)

    opinions = defaultdict(lambda: Avg())
    for tweet in tweets:
        words = get_words(tweet.text)
        said_nouns = filter(lambda v: v in nouns, words)
        op = opinion(words)
        for noun in said_nouns:
            opinions[noun].add(op)

    return {k: v.avg() for k, v in opinions.items() if v.avg_or(0) != 0}  # Return opinions, removing neutral opinons

