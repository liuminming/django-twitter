# Generated by Django 3.1.3 on 2023-06-12 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0003_tweetphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetphoto',
            name='comments_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='tweetphoto',
            name='likes_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
