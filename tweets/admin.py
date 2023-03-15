from django.contrib import admin
from tweets.models import Tweet


# the admin.py is to make it easier to manipulate data
@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )
