from testing.testcase import TestCase


class CommentModelTests(TestCase):

    def test_comment(self):
        user = self.create_user('alice')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertNotEqual(comment.__str__(), None)
