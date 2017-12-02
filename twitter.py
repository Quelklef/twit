
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

def tweets(search):
    """ Get tweets, bruh """
    return twitter.get("https://api.twitter.com/1.1/search/tweets.json", params={'q': search}).content.decode('utf-8')

def timeline(user):
    return 







