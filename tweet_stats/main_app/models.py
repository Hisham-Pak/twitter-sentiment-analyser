from django.db import models
import datetime
from django.db.models import Count
from datetime import timedelta,date

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=30, null=False, unique=True, db_index=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __str__(self):
        return f'{self.name}'

class CategoryDetail(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_details')
    created_date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    total_tweets = models.PositiveIntegerField(null=True, blank=True)
    total_positive = models.PositiveIntegerField(null=True, blank=True)
    total_negative = models.PositiveIntegerField(null=True, blank=True)
    total_alarming = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('-created',)
        get_latest_by = "created"

    def __str__(self):
        return f'{self.category}, {self.created}'

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategory')
    name = models.CharField(max_length=30, null=False, unique=True, db_index=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return f'{self.name}'

class SubCategoryDetail(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='subcategory_details')
    created_date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_tweets = models.PositiveIntegerField(null=True, blank=True)
    total_positive = models.PositiveIntegerField(null=True, blank=True)
    total_negative = models.PositiveIntegerField(null=True, blank=True)
    total_alarming = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.subcategory}, {self.created}'
    

class TweetManager(models.Manager):


    def get_tweets_by_category(self, category = "All", days = 7):

        """
        Returns an Array with the number of tweets for each day and category. If Category is not specified, it returns total number of tweets for each day
        """

        latesttweet = self.latest('tweet_date')
        date_list_for_table = []
        for i in range(days):
            date_list_for_table.append(latesttweet.tweet_date.date() - datetime.timedelta(days=i) )
        date_list=date_list_for_table[::-1]
        result = []

        if category is not None and category != "All":

            for i,date in enumerate(date_list):
                if (self.filter(category__name = category, tweet_day = date).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day')).exists()):
                    result.append(self.filter(category__name = category, tweet_day = date).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day'))[0]['count']) 
                else:
                    result.append(0)
        else:
            for i,date in enumerate(date_list):
                if (self.filter(tweet_day = date).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day')).exists()):
                    result.append(self.filter(tweet_day = date).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day')).filter(tweet_day = date)[0]['count']) 
                else:
                    result.append(0)
        return result

    def get_tweets_by_category_and_weeks(self, category = "All", weeks = 4):

    #It returns an Array with number of tweets for each weeks and category. If Category is not specified, it returns total number of tweets for each week.

        if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week")).count() >= weeks:
            weeklist = [Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]['tweet_week'] if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]  else 0 for x in
            range (weeks)][::-1]
        else:
            weeklist = [Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]['tweet_week'] if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]  else 0 for x in
            range (Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week")).count())][::-1]

        result = []

        if category is not None and category != "All":

            for week in weeklist:
                if (self.filter(category__name = category, tweet_week = week).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week')).exists()):
                    result.append(self.filter(category__name = category, tweet_week = week).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week'))[0]['count']) 
                else:
                    result.append(0)
        else:
            for week in weeklist:
                if (self.filter(tweet_week = week).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week')).exists()):
                    result.append(self.filter(tweet_week = week).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week')).filter(tweet_week = week)[0]['count']) 
                else:
                    result.append(0)
        return result


    def get_tweets_by_sentiment(self, category = "All", days = 7, sentiment="Positive"):

    #It returns an Array with number of tweets for each days (days), sentiment and category. If Category is not specified, it returns total number of tweets for each day.


        latesttweet = self.latest('tweet_date')
        date_list_for_table = []
        for i in range(days):
            date_list_for_table.append(latesttweet.tweet_date.date() - datetime.timedelta(days=i) )
        date_list=date_list_for_table[::-1]
        result = []

        if category is not None and category != "All":

            for i,date in enumerate(date_list):
                if (self.filter(category__name = category, tweet_day = date, tweet_sentiment = sentiment).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day')).exists()):
                    result.append(self.filter(category__name = category, tweet_day = date, tweet_sentiment = sentiment).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day'))[0]['count']) 
                else:
                    result.append(0)
        else:
            for i,date in enumerate(date_list):
                if (self.filter(tweet_day = date, tweet_sentiment = sentiment).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day')).exists()):
                    result.append(self.filter(tweet_day = date, tweet_sentiment = sentiment).values('tweet_day').order_by('-tweet_day').annotate(count = Count('tweet_day'))[0]['count']) 
                else:
                    result.append(0)
        return result

    def get_tweets_by_sentiment_and_weeks(self, category = "All", weeks = 4, sentiment="Positive"):

    #It returns an Array with number of tweets for each week, sentiment and category. If Category is not specified, it returns total number of tweets for each week.

        if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week")).count() >= weeks:
            weeklist = [Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]['tweet_week'] if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]  else 0 for x in
            range (weeks)][::-1]
        else:
            weeklist = [Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]['tweet_week'] if Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week"))[x]  else 0 for x in
            range (Tweets.objects.values('tweet_week').order_by('-tweet_week').annotate(Count("tweet_week")).count())][::-1]

        result = []

        if category is not None and category != "All":

            for week in weeklist:
                if (self.filter(category__name = category, tweet_week = week, tweet_sentiment = sentiment).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week')).exists()):
                    result.append(self.filter(category__name = category, tweet_week = week, tweet_sentiment = sentiment).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week'))[0]['count']) 
                else:
                    result.append(0)
        else:
            for week in weeklist:
                if (self.filter(tweet_week = week, tweet_sentiment = sentiment).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week')).exists()):
                    result.append(self.filter(tweet_week = week, tweet_sentiment = sentiment).values('tweet_week').order_by('-tweet_week').annotate(count = Count('tweet_week'))[0]['count']) 
                else:
                    result.append(0)
        return result

    

class Tweets(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    tweet_ID = models.BigIntegerField(unique = True)
    tweet_date = models.DateTimeField(db_index=True)
    tweet_day = models.DateField(db_index=True, null = True, default = date.today())
    tweet_week = models.IntegerField(default=201901, null=True, blank=True)
    tweet_username = models.CharField(max_length=100)
    tweet_content = models.TextField()
    tweet_URL = models.URLField()
    tweet_sentiment = models.CharField(max_length=50, db_index=True)
    created_date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    hasbeenreplied = models.BooleanField(default=False)
    objects = TweetManager()
    
    class Meta:
        ordering = ('-tweet_date',)
        verbose_name_plural = 'tweets'

    def __str__(self):
        return f'{self.sub_category}, {self.tweet_date  }, {self.tweet_ID}, {self.tweet_username}'

    def save(self, *args, **kwargs):
        if self.pk is not None and self.tweet_day is None:
            self.tweet_day = self.tweet_date.date()
        if self.pk is not None and self.tweet_day is not None:
            self.tweet_week = int(str(self.tweet_day.year) + str(self.tweet_day.isocalendar()[1]))
        super().save(*args, **kwargs)




