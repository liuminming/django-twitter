from testing.testcase import TestCase
from notifications.models import Notification

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'

class NotificationTests(TestCase):

    def setUp(self):
        self.alice, self.alice_client = self.create_user_and_client('alice')
        self.bob, self.bob_client = self.create_user_and_client('bob')
        self.bob_tweet = self.create_tweet(self.bob)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.alice_client.post(COMMENT_URL, {
            'tweet_id': self.bob_tweet.id,
            'content':'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.alice_client.post(LIKE_URL, {
            'content_type':'tweet',
            'object_id': self.bob_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)
