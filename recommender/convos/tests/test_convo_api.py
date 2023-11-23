from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APIClient
from suggestions.models import Convo
from suggestions.serializers import ConvoSerializer


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class ConvoViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='auth-user@example.com',
            password='auth-user-pass-123'
        )
        self.client.force_authenticate(self.user)
        self.convo = mommy.make(Convo, user=self.user)

    def test_list_convo(self):
        url = reverse('convos:convo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Assuming you have only one conversation in the database

    def test_retrieve_convo(self):
        url = reverse('convos:convo-detail', args=[str(self.convo.convo_id)]) # Use the actual conversation ID
        response = self.client.get(url)
        serializer = ConvoSerializer(self.convo)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_delete_convo(self):
        url = reverse('convos:convo-detail', args=[str(self.convo.convo_id)])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, 204)
        convo = Convo.objects.filter(user=self.user)
        self.assertFalse(convo.exists())

    def test_delete_all_convo(self):
        url = reverse('convos:convo-delete-all')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Convo.objects.filter(user=self.user).count(), 0)

    # Add more test cases for your viewset as needed
