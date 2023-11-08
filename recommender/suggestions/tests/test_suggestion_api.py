from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse

from suggestions.models import Convo, Snippet

from unittest.mock import patch

SUGGESTION_URL = reverse('suggestions:search')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class SuggestionApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='auth-user@example.com',
            password='auth-user-pass-123'
        )
        self.client.force_authenticate(self.user)

    def test_suggestion_initial_search(self):
        user = self.user
        res = self.client.get(SUGGESTION_URL)
        convo = Convo.objects.get(user=user)
        snippets = Snippet.objects.filter(convo=convo)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(snippets.count(), 2)
        self.assertEqual(snippets.filter(snippet_type="FRAMING").count(), 1)
        self.assertEqual(snippets.filter(snippet_type="ASSISTANT MESSAGE").count(), 1)
        self.assertEqual(snippets.count(), 2)



