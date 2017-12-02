
import twitter as tw
import json

from pprint import pprint

for tweet in tw.timeline('realDonaldTrump'):
    print(tweet)


