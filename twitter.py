
import json
from auth import sess

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

def timeline(identif, count=200):
    """ identif can be user id or user twitter handle (without '@') """
    assert count <= 200

    uid = name = None
    if type(identif) is int:
        uid = identif
    elif type(identif) is str:
        name = identif
    else:
        raise ValueError("Must be an int id or str handle")

    if uid: params = {'user_id': uid}
    else: params = {'screen_name': name}
    params.update({'count': count, 'tweet_mode': 'extended'})
    data = json.loads(twitter.get("https://api.twitter.com/1.1/statuses/user_timeline.json", params=params).content.decode('utf-8'))

    for tweet in data:
        yield Tweet(tweet)



