from django.urls import path
from . import views

app_name = 'main_app'

urlpatterns = [ 
    path('', views.dayplot, name='dayplot'),
    path('terms', views.terms, name='terms'),
    path('privacy', views.privacy, name='privacy'),
    path('plotfilter/', views.plotfilter, name='plotfilter'),
    path('plotfilter_for_week/', views.plotfilter_for_week, name='plotfilter_for_week'),
    path('tweets/', views.tweets_analysis, name='tweets_analysis'),
    path('tweets/<int:days>/', views.tweets_analysis, name='tweets_analysis_refresh'),
    path('tweets_detail/<str:sub_category>/', views.tweets_detail, name='tweets_detail'),

    #Reply feature

    path('reply/<int:tweet_ID>/', views.ReplyTweet, name="reply_tweet"),
    path('reply/<str:sub_category>/', views.ReplyPanel, name="reply_panel"),
    path('reply/<str:sub_category>/testjs', views.TestJs, name="testjs"),
    path('reply/<str:sub_category>/reply_with_image', views.TestJs, name="reply_with_image"),

        
    #db Migration. Used only once.

    path('tweets/migrate/days/', views.migrate_tweet_day, name='migrate_tweet_day'),
    path('tweets/migrate/weeks/', views.migrate_tweet_week, name='migrate_tweet_weeks'),
    

]