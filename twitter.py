
import requests as req
import requests_oauthlib as oauth

import tinydb
import json

#
# In auth.json put
# Consumer key and consumer secret
# Will ask for all else that is needed
#

with open('auth.json') as authf:
    auth = json.load(authf)

auth1 = oauth.OAuth1(auth['consumer_key'], auth['consumer_secret'])

if 'token' not in auth or 'secret' not in auth:
    if __name__ != "__main__":
        raise Exception("Have not generated token and secret. Please run as main module.")

    # Generate token + secret

    r = req.get("https://api.twitter.com/oauth/request_token", auth=auth1)
    key, secret = list(map(lambda s: s.split('=')[1], r.content.decode('utf-8').split('&')[:2]))

    print("Please authorize @ https://api.twitter.com/oauth/authorize?oauth_token=" + key)
    verif = input("Verifier: ")

    oauth2 = oauth.OAuth1(
            auth['consumer_key'],
            client_secret=auth['consumer_secret'],
            resource_owner_key=key,
            resource_owner_secret=secret,
            verifier=verif)

    cred = req.post("https://api.twitter.com/oauth/access_token", auth=oauth2)

    token, sec2 = list(map(lambda s: s.split('=')[1], cred.content.decode('utf-8').split('&')[:2]))

    auth['token'] = token
    auth['secret'] = sec2
    
    with open('auth.json', 'w') as authf:
        json.dump(auth, authf)

# Have token + secret

def sess():
    """ Return request session authenticated w/ twitter API """
    twitter = oauth.OAuth1Session(
            auth['consumer_key'],
            client_secret=auth['consumer_secret'],
            resource_owner_key=auth['token'],
            resource_owner_secret=auth['secret'])
    return twitter



twitter = sess()

users = dict()
class User:
    @staticmethod
    def get_or_create(uid, info):
        if uid in users:
            return users[uid]
        user = User(info)
        users[uid] = user
        return user

    def __init__(self, info):
        self.id = info['id']
        self.desc = info['description']
        self.name = info['name']

    def __str__(self):
        return str(self.__dict__)

    def timeline(self):
        return timeline(self.id)

class Tweet:
    def __init__(self, info):
        self.id = info['id']
        self.user = User.get_or_create(info['user']['id'], info['user'])
        self.text = info['full_text']

    def __str__(self):
        return str(self.__dict__)

def tweets(search):
    """ Get tweets, bruh """
    data = json.loads(twitter.get("https://api.twitter.com/1.1/search/tweets.json", params={'q': search, 'tweet_mode': 'extended'}).content.decode('utf-8'))
    for tweet in data['statuses']:
        yield Tweet(tweet)

def timeline(identif):
    """ identif can be user id or user twitter handle (without '@') """
    uid = name = None
    if type(identif) is int:
        uid = identif
    elif type(identif) is str:
        name = identif
    else:
        raise ValueError("Must be an int id or str handle")

    if uid: params = {'user_id': uid}
    else: params = {'screen_name': name}
    params.update({'tweet_mode': 'extended'})
    data = json.loads(twitter.get("https://api.twitter.com/1.1/statuses/user_timeline.json", params=params).content.decode('utf-8'))

    for tweet in data:
        yield Tweet(tweet)

