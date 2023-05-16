from accounts.models import UserProfile
from testing.testcase import TestCase


class UserProfileTests(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_profile_property(self):
        alice = self.create_user('alice')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = alice.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)