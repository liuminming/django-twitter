from django.contrib.auth.models import User
from testing.testcase import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):
    def setUp(self):
        self.alice = self.create_user('alice')
        self.tweet = self.create_tweet(self.alice, content='test')

    def test_hours_to_now(self):
        bob = User.objects.create_user(username='bob')
        tweet = Tweet.objects.create(user=bob, content='hello bob!')
        tweet .created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.alice, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.alice, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        bob = self.create_user('bob')
        self.create_like(bob, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        # 测试可以成功创建 photo 的数据对象
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.alice,
        )
        self.assertEqual(photo.user, self.alice)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)