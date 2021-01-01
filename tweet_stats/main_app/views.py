from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from .models import Category, SubCategory, CategoryDetail, SubCategoryDetail,Tweets
from .main import RetrieveTweetstoCSV
from .extract_text import *
from .replies import *
from .reply_to_tweet import *
from django.db.utils import IntegrityError
import time, datetime
from datetime import date, timedelta
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import tweepy
from django.core.files.storage import default_storage
import random, string

# Create your views here.

def terms(request):
    return render(request, 'main_app/terms.html', {})

def privacy(request):
    return render(request, 'main_app/privacy.html', {})

def tweets_analysis(request, *args, **kwargs):

    context = {}
    
    days = kwargs.get("days", None)

    if days is not None:
        start_date = datetime.date.today() - timedelta(days=days) 
        finish_date = datetime.date.today() + timedelta(days=1)
    
    categories = Category.objects.all()

    for category in categories:
 
        subcategories = SubCategory.objects.filter(category = category)

        for subcategory in subcategories:

            if start_date is not None and finish_date is not None:
      
                TweetList = TweetToList('#' + subcategory.name, start_date = start_date, finish_date = finish_date)

                AddSentimentToTweetList(TweetList)

                for tweet in TweetList:
                    try: 
                        new_tweet = Tweets.objects.create(category = category, sub_category = subcategory, tweet_ID = tweet[0], tweet_username = tweet[1], tweet_date = tweet[2], tweet_day = tweet[2].date(), tweet_content = tweet[3], tweet_URL = tweet[4], tweet_sentiment = tweet[5], tweet_week = int(str(tweet[2].year) + str(tweet[2].isocalendar()[1])))        
                        new_tweet.save() 
                    except IntegrityError:
                        print("Tweet with ID" + str(tweet[0]) + "already exists.")
                    except :
                        print("An unknow error has occurred.")



    messages.success(request, "Tweets successfuly updated!!")

    return render(request, 'main_app/tweets.html')


def tweets_detail(request, sub_category):
    subcategory = request.GET.get('sub_category.name', None)
    context = {}
    tweetlist = Tweets.objects.filter(sub_category__name = sub_category)
    context['tweetlist'] = tweetlist        
    return render(request, 'main_app/tweets_detail.html', context)

def dayplot(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    tweets_type = ["All", "Total positive", "Total negative", "Total alarming"]
    date_list_for_table = []
    days = 7
    weeks = 4

    try : 

        latesttweet = Tweets.objects.latest("tweet_date")

        for i in range(days):
            date_list_for_table.append(latesttweet.tweet_date.date() - datetime.timedelta(days=i) )

        date_list = date_list_for_table[::-1]

        if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week")).count() >= weeks:
            weeklist = [Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]['tweet_week'] if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]  else 0 for x in
    range (4)][::-1]
        else:
            weeklist = [Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]['tweet_week'] if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]  else 0 for x in
    range (Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week")).count())][::-1]

        weeklist = ["Week " + str(x)[4:6] for x in weeklist]

        #Data for Days Plot
        
        chart_data = Tweets.objects.get_tweets_by_category()
        positive_data = Tweets.objects.get_tweets_by_sentiment(sentiment="Positive")
        negative_data = Tweets.objects.get_tweets_by_sentiment(sentiment="Negative")
        alarming_data = Tweets.objects.get_tweets_by_sentiment(sentiment="Alarming")

        #Data for Weeks Plot
        
        chart_data2    = Tweets.objects.get_tweets_by_category_and_weeks()
        positive_data2 = Tweets.objects.get_tweets_by_sentiment_and_weeks(sentiment="Positive")
        negative_data2 = Tweets.objects.get_tweets_by_sentiment_and_weeks(sentiment="Negative")
        alarming_data2 = Tweets.objects.get_tweets_by_sentiment_and_weeks(sentiment="Alarming")

        #Data for Table 

        table_per_day = {}
        for subcategory in SubCategory.objects.all():
            table_per_day[subcategory.name] = {}
            tot_alarming = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_sentiment = "Alarming").aggregate(Count("tweets__tweet_sentiment"))["tweets__tweet_sentiment__count"]
            tot_positive = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_sentiment = "Positive").aggregate(Count("tweets__tweet_sentiment"))["tweets__tweet_sentiment__count"]
            tot_negative = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_sentiment = "Negative").aggregate(Count("tweets__tweet_sentiment"))["tweets__tweet_sentiment__count"]
            tot_tweets = tot_alarming + tot_positive + tot_negative

            if tot_alarming != 0:
                table_per_day[subcategory.name]['alarming'] = round(100*tot_alarming/tot_tweets,2)
            else:
                table_per_day[subcategory.name]['alarming'] = 0
            if tot_positive != 0:
                table_per_day[subcategory.name]['positive'] = round(100*tot_positive/tot_tweets,2)
            else:
                table_per_day[subcategory.name]['positive'] = 0

            if tot_negative != 0:
                table_per_day[subcategory.name]['negative'] = round(100*tot_negative/tot_tweets,2)
            else:
                table_per_day[subcategory.name]['negative'] = 0

            table_per_day[subcategory.name]['dia1'] = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_day = latesttweet.tweet_day).aggregate(Count('tweets__tweet_date'))['tweets__tweet_date__count']
            table_per_day[subcategory.name]['dia2'] = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_day = latesttweet.tweet_day - datetime.timedelta(days=1)).aggregate(Count('tweets__tweet_day'))['tweets__tweet_day__count']
            table_per_day[subcategory.name]['dia3'] = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_day = latesttweet.tweet_day - datetime.timedelta(days=2)).aggregate(Count('tweets__tweet_day'))['tweets__tweet_day__count']
            table_per_day[subcategory.name]['dia4'] = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_day = latesttweet.tweet_day - datetime.timedelta(days=3)).aggregate(Count('tweets__tweet_day'))['tweets__tweet_day__count']
            table_per_day[subcategory.name]['dia5'] = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_day = latesttweet.tweet_day - datetime.timedelta(days=4)).aggregate(Count('tweets__tweet_day'))['tweets__tweet_day__count']
            table_per_day[subcategory.name]['dia6'] = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_day = latesttweet.tweet_day - datetime.timedelta(days=5)).aggregate(Count('tweets__tweet_day'))['tweets__tweet_day__count']
            table_per_day[subcategory.name]['dia7'] = SubCategory.objects.filter(name = subcategory.name, tweets__tweet_day = latesttweet.tweet_day - datetime.timedelta(days=6)).aggregate(Count('tweets__tweet_day'))['tweets__tweet_day__count']

    except:

        date_list = []
        weeklist = []
        table_per_day = []
        positive_data = [] 
        negative_data = [] 
        alarming_data = [] 
        chart_data = [] 
        positive_data2 = [] 
        negative_data2 = [] 
        alarming_data2 = [] 
        chart_data2 = []


    context = {"categories": categories,  "date_list": date_list, 
               "tweets_type": tweets_type, "date_list_for_table" : date_list_for_table, 
               "subcategories": subcategories,  "weeklist" : weeklist, "table_per_day": table_per_day, 
               "chart_data": chart_data, "positive_data": positive_data, "negative_data": negative_data, "alarming_data": alarming_data,
               "chart_data2": chart_data2, "positive_data2": positive_data2, "negative_data2": negative_data2, "alarming_data2": alarming_data2,
               }

    return render(request, 'main_app/days.html', context)

def plotfilter(request):

    """
    Function that filters Week Plot Data for category. Called by Asynocronous JS when plot filters are clicked. Returns 
    new data in form of arrays for total, positive, negative and alarming tweets for a specific category. Chart in the 
    front-end is automatically updated with these data.
    """
    json_response = {'success' : False}

    category = request.GET.get("category", None)
    
    json_response['chart_data']    = Tweets.objects.get_tweets_by_category(category = category, days = 7)
    json_response['positive_data'] = Tweets.objects.get_tweets_by_sentiment(category = category, days = 7, sentiment="Positive")
    json_response['negative_data'] = Tweets.objects.get_tweets_by_sentiment(category = category, days = 7, sentiment="Negative")
    json_response['alarming_data'] = Tweets.objects.get_tweets_by_sentiment(category = category, days = 7, sentiment="Alarming")

    json_response['success'] = True


    return JsonResponse(json_response)

def plotfilter_for_week(request):

    """
    Function that filters Week Plot Data for category. Called by Asynocronous JS when plot filters are clicked. Returns 
    new data in form of arrays for total, positive, negative and alarming tweets for a specific category. Chart in the 
    front-end is automatically updated with these data.
    """
    json_response = {'success' : False}

    category = request.GET.get("category", None)
    
    json_response['chart_data2']    = Tweets.objects.get_tweets_by_category_and_weeks(category = category,  weeks = 4)
    json_response['positive_data2'] = Tweets.objects.get_tweets_by_sentiment_and_weeks(category = category, weeks = 4, sentiment="Positive")
    json_response['negative_data2'] = Tweets.objects.get_tweets_by_sentiment_and_weeks(category = category, weeks = 4, sentiment="Negative")
    json_response['alarming_data2'] = Tweets.objects.get_tweets_by_sentiment_and_weeks(category = category, weeks = 4, sentiment="Alarming")

    json_response['success'] = True


    return JsonResponse(json_response)

def migrate_tweet_day(request):
    for tweet in Tweets.objects.all():
        tweet.tweet_day = tweet.tweet_date.date()
        tweet.save()
    return True

def migrate_tweet_week(request):
    for tweet in Tweets.objects.all():
        tweet.tweet_week = int(str(tweet.tweet_day.year) + str(tweet.tweet_day.isocalendar()[1]))
        tweet.save()
    return True
    
# Reply features

def ReplyTweet(request, tweet_ID):
    try:
        tweet = Tweets.objects.get(tweet_ID = tweet_ID)
        Reply = "I'm not sure that 2 bonbons is the right solution for that. ¿are you?"
        ReplyToTweet(tweet_ID, "spassaro80", Reply)
    except Exception as e:
        print(str(e))
    
    return render(request, 'main_app/tweets.html')

def ReplyPanel(request, sub_category):
    try:
        tweetlist = Tweets.objects.filter(sub_category__name = sub_category)
        tweetlist_positive = Tweets.objects.filter(sub_category__name = sub_category, tweet_sentiment = "Positive")
        tweetlist_negative = Tweets.objects.filter(sub_category__name = sub_category, tweet_sentiment = "Negative")
        tweetlist_alarming = Tweets.objects.filter(sub_category__name = sub_category, tweet_sentiment = "Alarming")
    except Exception as e:
        print(str(e))
    context={}
    context['tweetlist'] = tweetlist
    context['tweets_type'] = ["All", "Positive", "Negative", "Alarming"] 
    context['tweetlist_positive'] = tweetlist_positive 
    context['tweetlist_negative'] = tweetlist_negative 
    context['tweetlist_alarming'] = tweetlist_alarming 
    context['sub_category'] = sub_category
    return render(request, 'main_app/tweets_reply_panel.html', context)


def TestJs(request, sub_category):

    if request.method == 'POST':

        custom_text = request.POST.get('custom_text')

        #Get what type of sentiment tweets we have to respond and append into "Sentiment_to_reply" List
        negative = request.POST.get('negative', None)
        positive = request.POST.get('positive', None)
        alarming = request.POST.get('alarming', None)
        custom_tweet = request.POST.get('custom_tweet', None)

        sentiment_to_reply = []
        if negative is not None:
            sentiment_to_reply.append('Negative') 
        if positive is not None:
            sentiment_to_reply.append('Positive') 
        if alarming is not None:
            sentiment_to_reply.append('Alarming')
        
        #Get all tweets to be replied, depending on the sentiment selected
        
        tweets_to_reply = Tweets.objects.filter(sub_category__name = sub_category, tweet_sentiment__in = sentiment_to_reply, hasbeenreplied = False)

        if len(tweets_to_reply) > 100:
            tweets_to_reply = tweets_to_reply[0:100]

        print(tweets_to_reply)
        number_of_tweets_sent = 0
        
        for index, tweet in enumerate(tweets_to_reply):
         
            #change the tweet text to have at least one random word and the twitter user in the text

            new_text = " ".join(custom_text.split(" ")[0:1]) + " " + tweet.tweet_username + " " +  " ".join(custom_text.split(" ")[1:]) +  " " + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
            print(custom_text)
        
            if request.FILES: #If there's an image upload image on server and send twitter with Image
                imagefile=request.FILES['tweet_file']
                file_name = default_storage.save(imagefile.name, imagefile)
                print(imagefile.name)
                number_of_tweets_sent += ReplyToTweetwithImage(tweet.tweet_ID, tweet.tweet_username, new_text, imagefile)
                time.sleep(60)

            
            else:              #Send a normal Twitter
                number_of_tweets_sent += ReplyToTweet(tweet.tweet_ID, tweet.tweet_username, new_text)
                time.sleep(60)
    
        messages.success(request, str(number_of_tweets_sent) + " Tweets have been succesfully replied")
        return redirect('main_app:dayplot')
    
    try:
        #Get number of tweets from the get request
        tweets = request.GET.get('content', "").split("-")

        #Get what type of sentiment tweets we have to respond and append into "Sentiment_to_reply" List
        negative = request.GET.get('negative', None)
        positive = request.GET.get('positive', None)
        alarming = request.GET.get('alarming', None)
        custom_tweet = request.GET.get('custom_tweet', None)
        custom_text = request.GET.get('text', None)
        if custom_text is not None:
            print(custom_text)
        sentiment_to_reply = []
        if negative is not None:
            sentiment_to_reply.append(negative) 
        if positive is not None:
            sentiment_to_reply.append(positive) 
        if alarming is not None:
            sentiment_to_reply.append(alarming)
        
        #Get all tweets to be replied, depending on the sentiment selected
        
        tweets_to_reply = Tweets.objects.filter(sub_category__name = sub_category, tweet_sentiment__in = sentiment_to_reply, hasbeenreplied = False)

        if len(tweets_to_reply) > 100:
            tweets_to_reply = tweets_to_reply[0:100]

        #1 loop through all tweets to be replied 
        #2 alternatevely select one tweet from tweets selected in the dashboard 
        #3 call ReplytoTweet to answer the tweet to be replied with the tweet to be replied username and the text from  selected tweets

        number_of_tweets_sent = 0

        for index, tweet in enumerate(tweets_to_reply):
            text=Tweets.objects.get(tweet_ID = tweets[index%len(tweets)]).tweet_content
            new_text = " ".join(text.split(" ")[0:1]) + " " + tweet.tweet_username + " " +  " ".join(text.split(" ")[1:]) +  " " + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
            number_of_tweets_sent += ReplyToTweet(tweet.tweet_ID, tweet.tweet_username, new_text)
            time.sleep(60)

        messages.success(request, str(number_of_tweets_sent) + " Tweets have been succesfully replied")
        return redirect('main_app:dayplot')

    except Exception as e:
        print(str(e))

    
