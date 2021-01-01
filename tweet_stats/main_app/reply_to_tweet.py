import tweepy
from .models import Tweets
from project.settings import consumer_key, consumer_secret, access_token, access_token_secret

"""Return the API  to send the Tweet"""

def GetTwitterApi():
    try:

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth, wait_on_rate_limit=True)
            
        return api
    
    except Exception as e:
        print(str(e))
        return 1

"""Post Reply"""

def ReplyToTweet(tweetID, UserName, Reply):
    try:

        api = GetTwitterApi()
        Msg = '@' + UserName + ' ' + Reply
        tweetposted = api.update_status(Msg, tweetID)
        print(tweetposted.id)
        tweet = Tweets.objects.get(tweet_ID = tweetID )
        tweet.hasbeenreplied = True
        tweet.save()
        return 1
    except Exception as e:
        print(str(e))
        return 0

"""Post Reply with Image"""

def ReplyToTweetwithImage(tweetID, UserName, Reply, imagefile):

    try:
        api = GetTwitterApi()
        res = api.media_upload('media/' + imagefile.name)
        media_id = res.media_id
        Msg = '@' + UserName + ' ' + Reply
        tweetposted = api.update_status(Msg, tweetID, media_ids=[media_id])
        print(tweetposted.id)
        tweet = Tweets.objects.get(tweet_ID = tweetID )
        tweet.hasbeenreplied = True
        tweet.save()        
        return 1
    except Exception as e:
        print(str(e))
        return 0

