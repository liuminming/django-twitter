from rest_framework.test import APIClient
from friendships.models import Friendship
from testing.testcase import TestCase

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.alice = self.create_user('alice')
        self.alice_client = APIClient()
        self.alice_client.force_authenticate(self.alice)

        self.bob = self.create_user('bob')
        self.bob_client = APIClient()
        self.bob_client.force_authenticate(self.bob)

        # create followings and followers for bob
        for i in range(2):
            follower = self.create_user('bob_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.bob)

        for i in range(3):
            following = self.create_user('bob_following{}'.format(i))
            Friendship.objects.create(from_user=self.bob, to_user=following)


    def test_list(self):
        #need log in
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # only get allowed
        response = self.alice_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # when there is not following
        response = self.alice_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # could see own tweet
        self.alice_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.alice_client.get(NEWSFEEDS_URL)
        print(response)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # alice following bob
        self.alice_client.post(FOLLOW_URL.format(self.bob.id))
        response = self.bob_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter'
        })
        posted_tweet_id = response.data['id']
        response = self.alice_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)