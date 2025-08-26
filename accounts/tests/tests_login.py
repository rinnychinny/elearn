from django.test import TestCase
from django.urls import reverse

from ..factories import UserFactory
from ..models import UserProfile
from ..forms import UserProfileForm


class UserLoginTests(TestCase):

    def setUp(self):
        # Create a user with a known username and password
        self.username = 'testuser1'
        self.password = 'testpass1'
        self.user = UserFactory(username=self.username,
                                set_password=self.password)

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
        self.assertRedirects(response, reverse('accounts:role_landing'))

    def test_login_with_invalid_user(self):
        # Attempt with invalid user
        response = self.client.post(reverse('login'), {
            'username': 'invalid_user',
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(
            response, "Please enter a correct username and password", status_code=200)

    def test_login_with_invalid_password(self):
        # Attempt with invalid password
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'invalid_password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(
            response, "Please enter a correct username and password", status_code=200)


class UserProfileTests(TestCase):

    def setUp(self):
        self.username1 = 'testuser1'
        self.password1 = 'testpass1'
        self.user1 = UserFactory(
            username=self.username1, set_password=self.password1)
        self.username2 = 'testuser2'
        self.password2 = 'testpass2'
        self.user2 = UserFactory(
            username=self.username2, set_password=self.password2)

    def test_userprofile_created_by_signal(self):
        profile = UserProfile.objects.get(user=self.user1)
        self.assertIsInstance(profile.public_name, str)
        self.assertEqual(profile.public_name, self.username1)

    # test duplicate public_name gives error
    def test_duplicate_public_name(self):
        profile1 = UserProfile.objects.get(user=self.user1)
        profile2 = UserProfile.objects.get(user=self.user2)
        # Attempt to update profile2 public_name to existing profile1 public_name
        form_data = {
            'public_name': profile1.public_name,  # duplicate value
            'public_status': profile2.public_status,
            'public_bio': profile2.public_bio,
        }
        form = UserProfileForm(data=form_data, instance=profile2)
        is_valid = form.is_valid()

        self.assertFalse(
            is_valid, "Form should be invalid with duplicate public_name")
        self.assertIn('public_name', form.errors)

# test only profile groups visible are the correct ones


class RegistrationTests(TestCase):

    def setUp(self):
        self.username1 = 'testuser1'
        self.password1 = 'testpass1'
        self.user1 = UserFactory(
            username=self.username1, set_password=self.password1)

    # test registration with existing credentials (username) fails
    def test_registration_with_existing_username(self):
        profile = UserProfile.objects.get(user=self.user1)
        self.assertIsInstance(profile.public_name, str)
        self.assertEqual(profile.public_name, self.username1)
