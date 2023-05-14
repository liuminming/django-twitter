from inbox.services import NotificationService
from testing.testcase import TestCase
from notifications.models import Notification


class NoificationServiceTests(TestCase):

    def setUp(self):
        self.alice = self.create_user('alice')
        self.bob = self.create_user('bob')
        self.alice_tweet = self.create_tweet(self.alice)

    def test_senf_comment_notification(self):
        # do not dispatch notification if tweet user == comment user
        comment = self.create_comment(self.alice, self.alice_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if tweet user != comment user
        comment = self.create_comment(self.bob, self.alice_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        # do not dispatch notification if tweet user == like user
        like = self.create_like(self.alice, self.alice_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # do not dispatch notification if tweet user != like user
        like = self.create_like(self.bob, self.alice_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)
