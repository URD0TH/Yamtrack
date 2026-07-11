"""Tests for the API history list endpoint."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from app.models import Item, MediaTypes, Movie, Sources, Status

MOCK_METADATA = {
    "title": "Test Movie",
    "image": "https://example.com/poster.jpg",
    "max_progress": 1,
    "related": {},
}


class HistoryApiTest(TestCase):
    """Test history list endpoint."""

    @patch("app.providers.services.get_media_metadata", return_value=MOCK_METADATA)
    def setUp(self, _mock_get_metadata):
        """Create a test user and a test movie."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )
        self.client.force_login(self.user)

        self.item = Item.objects.create(
            media_id="123",
            source=Sources.TMDB.value,
            media_type=MediaTypes.MOVIE.value,
            title="Test Movie",
            image="https://example.com/poster.jpg",
        )
        self.movie = Movie.objects.create(
            item=self.item,
            user=self.user,
            status=Status.COMPLETED.value,
        )

    def test_history_list(self):
        """Test listing change history for a media item."""
        response = self.client.get(
            "/api/history/tmdb/movie/123/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("timeline", response.data)
