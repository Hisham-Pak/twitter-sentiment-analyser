import tweepy
import pandas as pd
import numpy as np
import re, string
from facebook_scraper import get_posts
from stop_words import get_stop_words
from project.settings import consumer_key, consumer_secret, access_token, access_token_secret

stop_words = get_stop_words('french')
from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer
tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())

# Twitter Hastag
def TwitterHashtag(Hashtag, *args, **kwargs):

    start_date = kwargs.get("start_date", None) 
    finish_date = kwargs.get("finish_date", None) 
    since_id = kwargs.get("since_id", None) 

    try:

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        if start_date is not None and finish_date is not None:
        
            tweetdata = tweepy.Cursor(
                    api.search,
                    q=Hashtag,
                    count=1000,
                    since = start_date,
                    until = finish_date,
                    since_id = since_id
                ).items()
        else:
            tweetdata = tweepy.Cursor(
                    api.search,
                    q=Hashtag,
                    count=1000,
            ).items()

        TweetText = []

        # Merging Text in Single Variable
        for tweet in tweetdata:
            TweetText.append(
                [tweet.id,
                 tweet.user.screen_name,
                 tweet.created_at,
                 tweet.text,
                 f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"]
            )

        if len(TweetText) == 0:
            print("No Tweet Retrieved for Keyword: ", Hashtag)
            print()
            return None

        else:
            # Converting Tweet Text to Pandas DataFrame
            TweetDataFrame = pd.DataFrame(TweetText)
            TweetDataFrame.columns = ["Tweet_ID",  "User_Name", "Date Created", "Text", "URL"]
            return TweetDataFrame

    except Exception as e:
        print(str(e))

# Facebook Post
def FaceBookPost(KeyWord):
    try:
        PostText = []

        for post in get_posts(KeyWord, pages=10):
            PostText.append(post['text'])

        if len(PostText) == 0:
            print("No Post Retrieved")
            return

        else:
            # Converting Tweet Text to Pandas DataFrame
            PostDataFrame = pd.DataFrame(PostText)
            PostDataFrame.columns = ["Text"]

    except Exception as e:
        print(str(e))

# Text Cleaning
def Text_Preprocessing(text):
    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())
    text = re.sub(r'https?://[A-Za-z0-9./]+', '', text)
    text = "".join([char for char in text if char not in string.punctuation])
    text = re.sub('[0-9]+', '', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    Word_List = text.split()

    Filtered_Text = ''
    for words in Word_List:
        if not words.lower() in stop_words:
            Filtered_Text = Filtered_Text + ' ' + words

    text = Filtered_Text

    return text


import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Sentiment Analysis
def SentimentAnalysis(DataFrame):
    AlarmingWords = open(os.path.join(BASE_DIR, 'main_app/words.txt'), 'r').read().split()

    DataFrame['Sentiment'] = np.nan

    for i in range(len(DataFrame.index)):
        if len([word for word in AlarmingWords if (word.lower() in str(DataFrame.iloc[i, 3]).lower())]) > 0:
            DataFrame.iloc[i, 5] = 'Alarming'
        else:
            Temp = Text_Preprocessing(str(DataFrame.iloc[i, 3]))
            if len(Temp) > 0 or str(Temp) != 'nan':
                blob = tb(Temp)
                polarity_score = blob.sentiment[0]

                if polarity_score >= 0:
                    DataFrame.iloc[i, 5] = 'Positive'

                elif polarity_score < -0.70:
                    DataFrame.iloc[i, 5] = 'Alarming'

                else:
                    DataFrame.iloc[i, 5] = 'Negative'

def TweetToList(Hashtag, *args, **kwargs):

    start_date = kwargs.get("start_date", None) 
    finish_date = kwargs.get("finish_date", None) 
    since_id = kwargs.get("since_id", None) 

    try:

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        if start_date is not None and finish_date is not None:

            tweetdata = tweepy.Cursor(
                    api.search,
                    q=Hashtag,
                    count=1000,
                    since = start_date,
                    until = finish_date,
#                    since_id = since_id
                ).items()
        else:
            tweetdata = tweepy.Cursor(
                    api.search,
                    q=Hashtag,
                    count=1000,
            ).items()



        TweetText = []

        # Merging Text in Single Variable
        for tweet in tweetdata:
            TweetText.append(
                [tweet.id,
                 tweet.user.screen_name,
                 tweet.created_at,
                 tweet.text,
                 f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"]
            )

        if len(TweetText) == 0:
            print("No Tweet Retrieved for Keyword: ", Hashtag)

        return TweetText

    except Exception as e:
        print(str(e))

def AddSentimentToTweetList(TweetList):
    AlarmingWords = open(os.path.join(BASE_DIR, 'main_app/words.txt'), 'r').read().split()

    for tweet in TweetList:
        if len([word for word in AlarmingWords if (word.lower() in str(tweet[3]).lower())]) > 0:
            tweet.append('Alarming')
        else:
            Temp = Text_Preprocessing(str(tweet[3]))
            if len(Temp) > 0 or str(Temp) != 'nan':
                blob = tb(Temp)
                polarity_score = blob.sentiment[0]

                if polarity_score >= 0:
                    tweet.append('Positive')

                elif polarity_score < -0.70:
                    tweet.append('Alarming')

                else:
                    tweet.append('Negative')