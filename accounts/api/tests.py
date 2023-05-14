from testing.testcase import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from accounts.models import UserProfile

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            username = 'admin',
            email = 'admin@jiuzhang.com',
            password = 'correct password'
        )

    def test_login(self):
        # GET method is not allowed
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password'
        })

        self.assertEqual(response.status_code, 405)

        # use the wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password'
        })
        self.assertEqual(response.status_code, 400)

        # verify login status when not login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # use the correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')

        # verify after login successfully
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


    def test_logout(self):
        # login first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password'
        })

        # verify login user
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # GET method is not allowed
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # logout successfully after using POST
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # verify logout
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)


    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password'
        }

        # GET method is not allowed
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # incorrect email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        self.assertEqual(response.status_code, 400)

        # the length of password is too short
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123'
        })
        self.assertEqual(response.status_code, 400)

        # the length of username is too long
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone is tooooooooooooo looooooooooooooooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password'
        })
        self.assertEqual(response.status_code, 400)

        # signup successfully
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        # verify user profile is created
        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)

        # verify login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)



