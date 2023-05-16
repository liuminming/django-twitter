from testing.testcase import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.alice = self.create_user('alice')
        self.tweet = self.create_tweet(self.alice)
        self.comment = self.create_comment(self.alice, self.tweet)

    def test_comment(self):
        tweet = self.create_tweet(self.alice)
        comment = self.create_comment(self.alice, tweet)
        self.assertNotEqual(comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.alice, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.alice, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.bob = self.create_user('bob')
        self.create_like(self.bob, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
