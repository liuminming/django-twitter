from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcase import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'

class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.alice = self.create_user('alice')
        self.alice_client = APIClient()
        self.alice_client.force_authenticate(self.alice)

        self.bob = self.create_user('bob')
        self.bob_client = APIClient()
        self.bob_client.force_authenticate(self.bob)

        for i in range(2):
            follower = self.create_user('bob_follower{}'.format(i))
            Friendship.objects.create(from_user=follower,to_user=self.bob)

        for i in range(3):
            following = self.create_user('bob_following{}'.format(i))
            Friendship.objects.create(from_user=self.bob, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.alice.id)

        # can follow when authenticated
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # can only use post for follow
        response = self.bob_client.get(url)
        self.assertEqual(response.status_code, 405)
        # cannot follow yourself
        response = self.alice_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow successfully
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, 201)
        # repeating follow works silently
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, 400)
        # insert new data when following in an opposite way
        count = Friendship.objects.count()
        response = self.alice_client.post(FOLLOW_URL.format(self.bob.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.alice.id)

        # unauthenticated
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # GET method not allowed
        response = self.bob_client.get(url)
        self.assertEqual(response.status_code, 405)
        # cannot unfollow self
        response = self.alice_client.post(url)
        self.assertEqual(response.status_code, 400)
        # unfollow successfully
        Friendship.objects.create(from_user=self.bob, to_user=self.alice)
        count = Friendship.objects.count()
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)
        # unfollow when there is not such data
        count = Friendship.objects.count()
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_following(self):
        url = FOLLOWINGS_URL.format(self.bob.id)

        # POST is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # GET is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        # maintain time order
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'bob_following2'
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'bob_following1'
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'bob_following0'
        )

    def test_follower(self):
        url = FOLLOWERS_URL.format(self.bob.id)

        # POST is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # GET is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)

        # maintain time order
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'bob_follower1'
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'bob_follower0'
        )

