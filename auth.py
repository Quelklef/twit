import requests as req
import requests_oauthlib as oauth
from urllib.parse import parse_qs
import log
import json

# File contains twitter consumer and secret key as JSON
AUTH_JSON = "auth.json"

# Keys in said JSON
CONSUMER_KEY_STR = "consumer_key"
CONSUMER_SECRET_STR = "consumer_secret"
TOKEN_STR = "token"
SECRET_STR = "secret"
ALL_KEYS = (CONSUMER_KEY_STR, CONSUMER_SECRET_STR, TOKEN_STR, SECRET_STR)


def setup():
    """ Disclaimer: I don't know how OAuth works. """

    print("Go to https://apps.twitter.com/apps and click on or create your relevant app.")

    consumer_key = input("Twitter consumer key: ")
    consumer_secret = input("Twitter consumer secret: ")

    auth1 = oauth.OAuth1(consumer_key, consumer_secret)
    reply1 = req.get("https://api.twitter.com/oauth/request_token", auth=auth1)
    content1 = parse_qs(reply1.content.decode('utf-8'))
    resource_key = content1['oauth_token'][0]
    resource_secret = content1['oauth_token_secret'][0]

    verifier = input(f"Code from https://api.twitter.com/oauth/authorize?oauth_token={resource_key}: ")

    auth2 = oauth.OAuth1(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_key,
        resource_owner_secret=resource_secret,
        verifier=verifier
    )

    reply2 = req.post("https://api.twitter.com/oauth/access_token", auth=auth2)
    content2 = parse_qs(reply2.content.decode('utf-8'))
    token = content2['oauth_token'][0]
    secret = content2['oauth_token_secret'][0]

    auth = {
        CONSUMER_KEY_STR: consumer_key,
        CONSUMER_SECRET_STR: consumer_secret,
        TOKEN_STR: token,
        SECRET_STR: secret
    }

    with open(AUTH_JSON, 'w') as file:
        json.dump(auth, file)

    return auth


def valid_json():
    """ Whether or not the json file is as we want it """
    try:
        f = open(AUTH_JSON)
    except FileNotFoundError:
        return False

    with f:
        vals = json.load(f)
    return all(key in vals for key in ALL_KEYS)


if valid_json():
    if __name__ == "__main__":
        print("Everything is properly set up.")

    with open(AUTH_JSON) as f:
        auth = json.load(f)
else:
    if __name__ != '__main__':
        raise Exception(f"{AUTH_JSON} is invalid. Please run {__file__} as main module.")

    log.logger.info("Setting up authorization data...")
    auth = setup()


# Have token + secret
def sess():
    """ Return request session authenticated w/ Twitter API """
    return oauth.OAuth1Session(
            auth[CONSUMER_KEY_STR],
            client_secret=auth[CONSUMER_SECRET_STR],
            resource_owner_key=auth[TOKEN_STR],
            resource_owner_secret=auth[SECRET_STR]
    )


