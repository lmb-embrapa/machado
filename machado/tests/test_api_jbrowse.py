"""Tests JBrowse API."""
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase


class JBrowseTests(APITestCase, URLPatternsTestCase):
    """Ensure we access the JBrowse API endpoint."""

    urlpatterns = [
        path('api/', include('machado.api.urls')),
    ]

    def test_jbrowse_api(self):
        """Ensure we can retrieve JBrowse from the API endpoint."""
        url = reverse('jbrowse_global-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

#        url = reverse('jbrowse_features-list', args=['chrTest'])
#        response = self.client.get(url, format='json')
#        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('jbrowse_names-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('jbrowse_refseqs-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
