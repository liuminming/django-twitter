from rest_framework.test import APIClient

from testing.testcase import TestCase

LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_API = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'

class LikeApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
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

    def test_likes_in_comments_api(self):
        tweet = self.create_tweet(self.alice)
        comment = self.create_comment(self.alice, tweet)

        # test anonymous
        response = self.anonymous_client.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        # test comments list api
        response = self.bob_client.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.bob, comment)
        response = self.bob_client.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # test tweet detail api
        self.create_like(self.alice, comment)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.bob_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)


    def test_likes_in_tweets_api(self):
        tweet = self.create_tweet(self.alice)

        # test tweet detail api
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.bob_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.bob, tweet)
        response = self.bob_client.get(url)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        # test tweets list api
        response = self.bob_client.get(TWEET_LIST_API, {'user_id': self.alice.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'], True)
        self.assertEqual(response.data['results'][0]['likes_count'], 1)

        # test newsfeeds list api
        self.create_like(self.alice, tweet)
        self.create_newsfeed(self.bob, tweet)
        response = self.bob_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['has_liked'], True)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 2)

        # test likes details
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.bob_client.get(url)
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(response.data['likes'][0]['user']['id'], self.alice.id)
        self.assertEqual(response.data['likes'][1]['user']['id'], self.bob.id)

    def test_likes_count(self):
        tweet = self.create_tweet(self.alice)
        data = {'content_type': 'tweet', 'object_id': tweet.id}
        self.alice_client.post(LIKE_BASE_URL, data)

        tweet_url = TWEET_DETAIL_API.format(tweet.id)
        response = self.alice_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 1)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 1)

        # cancel likes
        self.alice_client.post(LIKE_BASE_URL + 'cancel/', data)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 0)
        response = self.bob_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 0)

    def test_likes_count_with_cache(self):
        tweet = self.create_tweet(self.alice)
        self.create_newsfeed(self.alice, tweet)
        self.create_newsfeed(self.bob, tweet)

        data = {'content_type': 'tweet', 'object_id': tweet.id}
        tweet_url = TWEET_DETAIL_API.format(tweet.id)
        for i in range(3):
            _, client = self.create_user_and_client('someone{}'.format(i))
            client.post(LIKE_BASE_URL, data)
            # check tweet api
            response = client.get(tweet_url)
            self.assertEqual(response.data['likes_count'], i + 1)
            tweet.refresh_from_db()
            self.assertEqual(tweet.likes_count, i + 1)

        self.bob_client.post(LIKE_BASE_URL, data)
        response = self.bob_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 4)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 4)

        # check newsfeed api
        newsfeed_url = '/api/newsfeeds/'
        response = self.alice_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 4)
        response = self.bob_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 4)

        # bob canceled likes
        self.bob_client.post(LIKE_BASE_URL + 'cancel/', data)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 3)
        response = self.bob_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 3)
        response = self.alice_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 3)
        response = self.bob_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 3)



