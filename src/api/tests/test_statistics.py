"""Tests for the API statistics endpoint."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

MOCK_STATS = {
    "media_count": {},
    "media_type_distribution": [],
    "score_distribution": {},
    "top_rated": [],
    "status_distribution": {},
    "status_pie_chart_data": [],
    "timeline": [],
    "activity_data": [],
}


@patch("app.statistics.get_user_media", return_value=([], {}))
@patch("app.statistics.get_media_type_distribution", return_value=[])
@patch("app.statistics.get_score_distribution", return_value=({}, []))
@patch("app.statistics.get_status_distribution", return_value={})
@patch("app.statistics.get_status_pie_chart_data", return_value=[])
@patch("app.statistics.get_timeline", return_value=[])
@patch("app.statistics.get_activity_data", return_value=[])
class StatisticsApiTest(TestCase):
    """Test the statistics endpoint."""

    def setUp(self):
        """Create a test user and log in."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {self.user.token}"

    def test_statistics(self, *_args):
        """Test getting aggregated statistics."""
        response = self.client.get("/api/statistics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("media_count", response.data)
