import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    keys = loadkeys(twitter_auth_filename)
    consumer_key = keys[0]
    consumer_secret = keys[1]
    token = keys[2]
    token_secret = keys[3]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    tweets = []
    tw_dic = {}
    sid = SentimentIntensityAnalyzer()
    statuses = api.user_timeline(screen_name=name, count=100)
    for status in statuses:
        dic = {}
        dic['id'] = status.id
        dic['created'] = status.created_at.strftime('%Y-%m-%d')
        dic['retweeted'] = status.retweet_count
        dic['text'] = status.text
        dic['hashtags'] = status.entities['hashtags']
        dic['urls'] = status.entities['urls']
        dic['mentions'] = [mention['screen_name'] for mention in status.entities['user_mentions']]
        dic['score'] = sid.polarity_scores(status.text)['compound']
        tweets.append(dic)
    tw_dic['user'] = name
    tw_dic['count'] = api.get_user(name).statuses_count
    tw_dic['tweets'] = tweets
    return tw_dic

def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """
    friend_id = api.friends_ids(name, count=100)
    followed=[]
    for id in friend_id:
        user = api.lookup_users(user_ids=[id])[0]
        dic={}
        dic['name'] = user.name
        dic['screen_name'] = user.screen_name
        dic['followers'] = user.followers_count
        dic['created'] = user.created_at.strftime('%Y-%m-%d')
        dic['image'] = user.profile_image_url
        followed.append(dic)
    return followed