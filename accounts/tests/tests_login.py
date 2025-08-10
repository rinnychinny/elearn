from django.test import TestCase
from django.urls import reverse
from ..factories import UserFactory, UserProfileFactory

class UserLoginTests(TestCase):

    def setUp(self):
        # Create a user with a known username and password
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = UserFactory(username=self.username, set_password=self.password)

    def test_login_with_factory_user(self):
        # Attempt to login using the test client
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)

    def test_userprofile_factory_creates_profile(self):
        # Create a user profile for the factory user
        profile = UserProfileFactory(user=self.user)
        self.assertEqual(profile.user.username, self.username)
        self.assertIsInstance(profile.public_bio, str)
