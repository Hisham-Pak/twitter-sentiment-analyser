from django.contrib import admin
from main_app.models import *
from . import models
# Register your models here.

class TweetsAdmin(admin.ModelAdmin):
    model = Tweets
    list_filter = ('category' ,'sub_category', 'tweet_sentiment',"tweet_date")

admin.site.register(models.Category)
admin.site.register(models.CategoryDetail)
admin.site.register(models.SubCategory)
admin.site.register(models.SubCategoryDetail)
admin.site.register(Tweets, TweetsAdmin)