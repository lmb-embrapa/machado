"""Tests organism API."""
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase


class OrganismTests(APITestCase, URLPatternsTestCase):
    """Ensure we access the organism API endpoint."""

    urlpatterns = [
        path('api/', include('machado.api.urls')),
    ]

    def test_organism_api(self):
        """Ensure we can retrieve organisms from the API endpoint."""
        url = reverse('organism-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
