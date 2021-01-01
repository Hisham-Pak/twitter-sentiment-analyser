import tweepy
from project.settings import consumer_key, consumer_secret, access_token, access_token_secret

# Reply Tweet
def ReplyTweet(DataFrame, Reply=None):
    Negative_Tweets = DataFrame.loc[DataFrame['Sentiment'] == 'Negative']
    Alarming_Tweets = DataFrame.loc[DataFrame['Sentiment'] == 'Alarming']

    ReplyLimit = 3
    Reply_count = 0

    if Reply is None:
        Positive_Reply_Index = 0
        Positive_Tweets = DataFrame.loc[DataFrame['Sentiment'] == 'Positive']

        for i in range(len(Negative_Tweets)):
            if Reply_count < ReplyLimit:
                if Positive_Reply_Index >= len(Positive_Tweets.index):
                    Positive_Reply_Index = 0
                ReplyToTweet(Negative_Tweets.iloc[i, 0], Negative_Tweets.iloc[i, 1], Positive_Tweets.iloc[Positive_Reply_Index, 2])
                Positive_Reply_Index += 1
                Reply_count += 1
            else:
                break

        for i in range(len(Alarming_Tweets)):
            if Reply_count < ReplyLimit:
                if Positive_Reply_Index >= len(Positive_Tweets.index):
                    Positive_Reply_Index = 0
                ReplyToTweet(Alarming_Tweets.iloc[i, 0], Alarming_Tweets.iloc[i, 1], Positive_Tweets.iloc[Positive_Reply_Index, 2])

                Positive_Reply_Index += 1
                Reply_count += 1
            else:
                break

    else:
        for i in range(len(Negative_Tweets)):
            if Reply_count < ReplyLimit:
                ReplyToTweet(Negative_Tweets.iloc[i, 0], Negative_Tweets.iloc[i, 1], Reply)
                Reply_count += 1
            else:
                break

        for i in range(len(Alarming_Tweets)):
            if Reply_count < ReplyLimit:
                ReplyToTweet(Alarming_Tweets.iloc[i, 0], Alarming_Tweets.iloc[i, 1], Reply)
                Reply_count += 1
            else:
                break

# Post Reply
def ReplyToTweet(tweetID, UserName, Reply):
    try:

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth, wait_on_rate_limit=True)

        Msg = '@' + UserName + ' ' + Reply

        api.update_status(Msg, tweetID)

    except Exception as e:
        print(str(e))