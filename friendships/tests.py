from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcase import TestCase


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.alice = self.create_user('alice')
        self.bob = self.create_user('bob')

    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.bob]:
            Friendship.objects.create(from_user=self.alice, to_user=to_user)
        FriendshipService.invalidate_following_cache(self.alice.id)

        user_id_set = FriendshipService.get_following_user_id_set(self.alice.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.bob.id})

        Friendship.objects.filter(from_user=self.alice, to_user=self.bob).delete()
        FriendshipService.invalidate_following_cache(self.alice.id)
        user_id_set = FriendshipService.get_following_user_id_set(self.alice.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})