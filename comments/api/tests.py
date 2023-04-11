from django.utils import timezone
from rest_framework.test import APIClient
from comments.models import Comment
from testing.testcase import TestCase

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'

class CommentApiTests(TestCase):

    def setUp(self):
        self.alice = self.create_user('alice')
        self.alice_client = APIClient()
        self.alice_client.force_authenticate(self.alice)
        self.bob = self.create_user('bob')
        self.bob_client = APIClient()
        self.bob_client.force_authenticate(self.bob)

        self.tweet = self.create_tweet(self.alice)

    def test_create(self):
        # anonymous is not allowed
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        #bad request when having no param values
        response = self.alice_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        #bad request when only having tweet id
        response = self.alice_client.post(COMMENT_URL, {'tweet_id':self.tweet.id})
        self.assertEqual(response.status_code, 400)

        #bad request when only having content
        response = self.alice_client.post(COMMENT_URL, {'content':'hello'})
        self.assertEqual(response.status_code, 400)

        # content should no be too long
        response = self.alice_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1'*141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        #success
        response = self.alice_client.post(COMMENT_URL, {
            'tweet_id':self.tweet.id,
            'content':'1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.alice.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_destroy(self):
        comment = self.create_comment(self.alice, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)

        #anonymous is not allowed
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        #only object owner could delete object
        response = self.bob_client.delete(url)
        self.assertEqual(response.status_code, 403)

        #object owner deletes object
        count = Comment.objects.count()
        response = self.alice_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.alice, self.tweet, 'old')
        another_tweet = self.create_tweet(self.bob)
        url = COMMENT_DETAIL_URL.format(comment.id)

        #anonymous is not allowed
        response = self.anonymous_client.put(url, {'content':"new"})
        self.assertEqual(response.status_code, 403)

        #only object owner could update object
        response = self.bob_client.put(url, {'content':'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')

        #only content is updated
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.alice_client.put(url, {
            'content':'new',
            'user_id':self.alice.id,
            'tweet_id':another_tweet.id,
            'create_at':now
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.alice)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)


