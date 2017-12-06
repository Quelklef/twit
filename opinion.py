
import json
import twitter
from collections import defaultdict


class Avg:
    """ Represents a collections of numbers.
    Why? Because using tuples isn't as expressive. """

    def __init__(self, sum_=0, count=0):
        self.sum = sum_
        self.count = count

    def add(self, n):
        self.sum += n
        self.count += 1

    def avg(self):
        return self.sum / self.count

    def avg_or(self, val):
        if self.count == 0:
            return val
        return self.avg()

    def __str__(self):
        return "avg: " + str(self.avg())

    def __repr__(self):
        return "[avg {}]".format(self.avg())


with open('words.json') as wordsf:
    words = json.load(wordsf)
positive = set(words['positive'])
negative = set(words['negative'])
nouns = set(words['noun'])


def remove_chars(string, chars):
    ret = ""
    for c in string:
        if c not in chars:
            ret += c
    return ret


def get_words(sentence):
    sentence = sentence.replace('\n', ' ')
    sentence = remove_chars(sentence, "\"'~!@#$%^&*()`1234567890-_=+<>,.?/;:\\|[]{}")
    sentence = sentence.lower().split(' ')
    sentence = filter(lambda v: v != '', sentence)
    return list(sentence)


def opinion(words_li):
    if type(words_li) is not list:
        raise ValueError("You're probably calling opinon(string). Call opinion(get_words(string))")
    if not words_li: return 0
    op = 0
    for word in words_li:
        if word in positive: op += 1
        elif word in negative: op -= 1
    return float(op) / len(words_li)


def profile(uid):
    """ Profile a user's opinion.
    Iterates through 200 recent user tweets and
    catalogues the user's opinion of all (significant (todo))
    words said in the timeline. """
    tweets = twitter.timeline(uid, 200)

    opinions = defaultdict(lambda: Avg())
    for tweet in tweets:
        words_li = get_words(tweet['text'])
        said_nouns = filter(lambda v: v in nouns, words_li)
        op = opinion(words_li)
        for noun in said_nouns:
            opinions[noun].add(op)

    return {k: v.avg() for k, v in opinions.items() if v.avg_or(0) != 0}  # Return opinions, removing neutral opinons

