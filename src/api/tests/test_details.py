"""Tests for the API details endpoints."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

SEASON_METADATA = {
    "image": "https://example.com/season1.jpg",
    "episodes": [{"episode_number": 1, "still_path": None}],
}

TV_METADATA = {
    "title": "Test TV Show",
    "image": "https://example.com/tv.jpg",
    "max_progress": 24,
    "season/1": SEASON_METADATA,
    "related": {},
}

MOVIE_METADATA = {
    "title": "Test Movie",
    "image": "https://example.com/poster.jpg",
    "max_progress": 1,
    "related": {},
}


def get_metadata_side_effect(media_type, *args, **kwargs):  # noqa: ARG001
    """Return different mock data based on media type."""
    if media_type == "tv_with_seasons":
        return TV_METADATA
    return MOVIE_METADATA


class DetailsApiTest(TestCase):
    """Test metadata details and season details endpoints."""

    def setUp(self):
        """Create a test user."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {self.user.token}"

    @patch(
        "app.providers.services.get_media_metadata",
        side_effect=get_metadata_side_effect,
    )
    def test_details(self, _mock_get_metadata):
        """Test getting metadata details for a media item."""
        response = self.client.get("/api/details/tmdb/movie/123/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)

    @patch(
        "app.providers.services.get_media_metadata",
        side_effect=get_metadata_side_effect,
    )
    def test_season_details(self, _mock_get_metadata):
        """Test getting season metadata details."""
        response = self.client.get(
            "/api/details/tmdb/tv/123/season/1/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
