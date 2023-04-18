from testing.testcase import TestCase

LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'

class LikeApiTests(TestCase):

    def setUp(self):
        self.alice, self.alice_client = self.create_user_and_client('alice')
        self.bob, self.bob_client = self.create_user_and_client('bob')

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.alice)
        data = {'content_type': 'tweet', 'object_id':tweet.id}

        #anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        #get is not allowed
        response = self.alice_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.alice_client.post(LIKE_BASE_URL, {
            'content_type': 'twet',
            'object_id': tweet.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong content_type
        response = self.alice_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': -1
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        #post success
        response = self.alice_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        #duplicate likes
        self.alice_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.bob_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_likes(self):
        tweet = self.create_tweet(self.alice)
        comment = self.create_comment(self.alice, tweet)
        data = {'content_type': 'comment', 'object_id':comment.id}

        #anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        #get is not allowed
        response = self.alice_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        #wrong content_type
        response = self.alice_client.post(LIKE_BASE_URL, {
            'content_type': 'coment',
            'object_id':comment.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong content_type
        response = self.alice_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        #post success
        response = self.alice_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        #duplicate likes
        self.alice_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 1)
        self.bob_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        tweet = self.create_tweet(self.alice)
        comment = self.create_comment(self.bob, tweet)
        like_comment_data = {'content_type': 'comment', 'object_id':comment.id}
        like_tweet_data = {'content_type':'tweet', 'object_id':tweet.id}
        self.alice_client.post(LIKE_BASE_URL, like_comment_data)
        self.bob_client.post(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        #login required
        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        #get is not allowed
        response = self.alice_client.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)

        #wrong content_type
        response = self.alice_client.post(LIKE_CANCEL_URL, {
            'content_type':'wrong',
            'object_id': 1,
        })
        self.assertEqual(response.status_code, 400)

        # wrong object_id
        response = self.alice_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)

        #alice has not liked before
        response = self.alice_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # bob has not liked before
        response = self.bob_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        #successfully canceled
        response = self.alice_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        response = self.bob_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)





