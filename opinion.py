
import json
import twitter
from misc import Avg
from collections import defaultdict

with open('words.json') as wordsf:
    words = json.load(wordsf)
positive = set(words['positive'])
negative = set(words['negative'])
insignif = set(words['insignif'])

def removeChars(string, chars):
    ret = ""
    for c in string:
        if c not in chars:
            ret += c
    return ret

def is_significant_word(word):
    """ Remove stuff like "is", "of", "and", etc.
    Also do some other things because stuff. """
    if word in insignif: return False
    if word.startswith('http'): return False  # this was becoming a problem
    return True

def get_words(sentence):
    sentence = sentence.replace('\n', ' ')
    sentence = removeChars(sentence, "\"'~!@#$%^&*()`1234567890-_=+<>,.?/;:\\|[]{}")
    sentence = sentence.lower().split(' ')
    sentence = filter(lambda v: v != '', sentence)
    sentence = filter(is_significant_word, sentence)
    return list(sentence)

def opinion(words):
    if not words: return 0
    op = 0
    for word in words:
        if word in positive: op += 1
        elif word in negative: op += 1
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
        op = opinion(words)
        for word in words:
            opinions[word].add(op)

    return opinions



if __name__ == "__main__":
    for tweet in twitter.tweets('realDonaldTrump'):
        print(profile(tweet.user))




