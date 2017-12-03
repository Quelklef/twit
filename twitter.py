
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

    @staticmethod
    def from_name(name):
        return User(json.loads(twitter.get("https://api.twitter.com/1.1/users/lookup.json", params={'screen_name': name}).content.decode('utf-8'))[0])

    @staticmethod
    def from_id(uid):
        return User(json.loads(twitter.get("https://api.twitter.com/1.1/users/lookup.json", params={"user_id": uid}).content.decode('utf-8'))[0])

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

def timeline(user, count):
    """ identif can be user id or user twitter handle (without '@') """
    assert count <= 200

    params = {'count': count, 'tweet_mode': 'extended', 'user_id': user.id}
    data = json.loads(twitter.get("https://api.twitter.com/1.1/statuses/user_timeline.json", params=params).content.decode('utf-8'))

    for tweet in data:
        if type(tweet) is dict:  # For some reason was str
            yield Tweet(tweet)


def realtime(query): 
    while True:
        current = ""
        datastream = twitter.get("https://stream.twitter.com/1.1/statuses/filter.json", params={'track': query, 'tweet_mode': 'extended'}, stream=True)
        lineiterator = datastream.iter_lines()
        while True:
            try:
                line = next(lineiterator)
            except StopIteration:
                break
            except Exception as e:
                print("Error @ datastream loop:\n{}".format(e))
            
            if not line: continue
            current += line.decode('utf-8')

            try:
                tweet_dict = json.loads(current)
            except ValueError:
                pass
            else:
                if not 'text' in tweet_dict: continue  # Happens for some reason idk
                tweet_dict['full_text'] = tweet_dict['text']  # extended mode doesn't seem to be working
                yield Tweet(tweet_dict)
                current = ""

if __name__ == "__main__":
    for item in realtime("realDonaldTrump"):
        input(item)





