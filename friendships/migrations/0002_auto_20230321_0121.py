# Generated by Django 3.1.3 on 2023-03-21 01:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friendships', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FriendshipModel',
            new_name='Friendship',
        ),
    ]