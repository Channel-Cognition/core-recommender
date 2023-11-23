import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUsrApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'email': 'test@example.com',
            'password': 'test_pass123',
            'name': 'AnonymousUser'
        }

    def test_create_user_success(self):
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.payload['email'])

        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', res.data)

    def test_with_email_exists_error(self):
        create_user(**self.payload)
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def password_too_short_error(self):
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=self.payload.get('email')
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        user_details = {
            'name': 'Test name',
            'email': 'test_@example.com',
            'password': 'test-user-password123'
        }
        create_user(**user_details)

        credentials = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, credentials)
        self.assertEqual(res['Content-Type'], 'application/json')
        data = json.loads(res.content)
        self.assertIn('token', data[0])

    def test_create_token_bad_credentials(self):
        create_user(email='test1@example.com',
                    password='good-password'
                    )

        credentials = {
            'email': 'test1@example.com',
            'password': 'bad-pass'
        }
        res = self.client.post(TOKEN_URL, credentials)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        credentials = {
            'email': 'test1@example.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, credentials)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUerApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test_@example.com',
            password='auth-user-super-pass123',
            name='AuthUser'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                'id': self.user.pk,
                'name': self.user.name,
                'email': self.user.email
            }
        )

    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        credentials = {
            'name': 'Updated name',
            'password': 'updated-password-123'
        }

        res = self.client.patch(ME_URL, credentials)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, credentials['name'])
        self.assertTrue(self.user.check_password(credentials['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)