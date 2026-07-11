"""Tests for the API search endpoint."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status


class SearchApiTest(TestCase):
    """Test external provider search endpoints."""

    def setUp(self):
        """Create a test user."""
        self.testpass = "testpass123"
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.testpass,
        )
        self.client.force_login(self.user)

    @patch("app.providers.services.search")
    def test_search_requires_query(self, mock_search):  # noqa: ARG002
        """Test that search without query returns 400."""
        response = self.client.get("/api/search/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("app.providers.services.search")
    def test_search_returns_results(self, mock_search):
        """Test that search returns results from external provider."""
        mock_search.return_value = {
            "results": [
                {
                    "media_id": "1",
                    "title": "Test Result",
                    "media_type": "movie",
                    "source": "tmdb",
                    "image": "",
                },
            ],
            "page": 1,
            "total_results": 1,
            "total_pages": 1,
        }
        response = self.client.get("/api/search/?q=test&media_type=movie")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
