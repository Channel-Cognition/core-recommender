from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.encoding import force_bytes
from unittest.mock import patch
from model_mommy import mommy
from rest_framework.test import APIRequestFactory, force_authenticate
from suggestions.views import SearchListView
from suggestions.models import Convo, Snippet


class SearchListViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = mommy.make(get_user_model())
        self.convo = mommy.make(Convo, user=self.user)

    @patch('suggestions.views.perform_search')
    @patch('suggestions.views.get_or_create_image_cache')
    def test_search_list_view(self, mock_get_or_create_image_cache, mock_perform_search):
        query = "Your test query"
        convo_id = self.convo.convo_id
        snipper = mommy.make(Snippet, convo=self.convo)

        mock_perform_search.return_value = {
            "MESSAGE_STATUS": "SUCCESS",
            "MESSAGE_DATA": {
                "llm_response": "Your mock response",
                "items": [{"thumbnail_url": "mocked_image_url"}]
            }
        }
        mock_get_or_create_image_cache.return_value = {
            "image_b64_medium": "mocked_image_data"
        }
        request = self.factory.get('/api/suggestions/', {'q': query, 'convo_id': convo_id})

        view = SearchListView.as_view()
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, 200)
        response.render()
        content = force_bytes(response.content)

        self.assertIn(b'Your mock response', response.content)


        mock_perform_search.assert_called_once_with(query, str(convo_id))
        mock_get_or_create_image_cache.assert_called_once_with("mocked_image_url")
