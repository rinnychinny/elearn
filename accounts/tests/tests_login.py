from django.test import TestCase
from django.urls import reverse

from ..factories import UserFactory
from ..models import UserProfile

class UserLoginTests(TestCase):

    def setUp(self):
        # Create a user with a known username and password
        self.username = 'testuser1'
        self.password = 'testpass1'
        self.user = UserFactory(username=self.username, set_password=self.password)

    def test_login_with_valid_user(self):
        # Attempt with valid user
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        # should be a redirect
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

        # check redirect location is correct
        self.assertRedirects(response, reverse('role_landing'))

    def test_login_with_invalid_user(self):
        # Attempt with invalid user
        response = self.client.post(reverse('login'), {
            'username': 'invalid_user',
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(response, "Please enter a correct username and password", status_code=200)

    def test_login_with_invalid_password(self):
        # Attempt with invalid password
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'invalid_password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(response, "Please enter a correct username and password", status_code=200)

class UserProfileTests(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'testpass1'
        self.user = UserFactory(username=self.username, set_password=self.password)

    def test_userprofile_created_by_signal(self):
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsInstance(profile.public_name, str) 
        self.assertEqual(profile.public_name, self.username)
