from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django.db.utils import IntegrityError
from django_apscheduler.models import DjangoJobExecution
from main_app.models import Category, SubCategory, CategoryDetail, SubCategoryDetail,Tweets
from main_app.main import RetrieveTweetstoCSV
from main_app.extract_text import *
import datetime
from datetime import date, timedelta
import sys

# This is the function you want to schedule - add as many as you want and then register them in the start() function below

def update_tweets_hourly():
    
    start_date = datetime.date.today() - timedelta(days=3)   
    finish_date = datetime.date.today() + timedelta(days=1) 
    categories = Category.objects.all()

    for category in categories:
 
        subcategories = SubCategory.objects.filter(category = category)

        for subcategory in subcategories:

            try:

                TweetList = TweetToList('#' + subcategory.name, start_date = start_date, finish_date = finish_date)

                AddSentimentToTweetList(TweetList)

                for tweet in TweetList:
                    try: 
                        new_tweet = Tweets.objects.create(category = category, sub_category = subcategory, tweet_ID = tweet[0], tweet_username = tweet[1], tweet_date = tweet[2], tweet_day = tweet[2].day(), tweet_content = tweet[3], tweet_URL = tweet[4], tweet_sentiment = tweet[5], tweet_week = int(str(tweet[2].year) + str(tweet[2].isocalendar()[1])))        
                        new_tweet.save() 
                    except IntegrityError:
                        print("Tweet with ID" + str(tweet[0]) + "already exists.")
                    except :
                        print("An unknow error has occurred.")
            except:
                print("Couldn't update Tweets for " + str(subcategory.name))

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 1 hours
    scheduler.add_job(update_tweets_hourly, 'interval', minutes=60, name='update_tweets_hourly', id="update_tweets_hourly", max_instances= 1, replace_existing=True, jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)