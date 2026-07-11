"""Tests for the API authentication endpoints."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status


class AuthTest(TestCase):
    """Test JWT token authentication."""

    def setUp(self):
        """Create a test user."""
        self.testpass = "testpass123"
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.testpass,
        )

    def test_token_obtain_with_valid_credentials(self):
        """Test obtaining a JWT token with valid email and password."""
        response = self.client.post(
            "/api/token/",
            {"email": "test@example.com", "password": self.testpass},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_obtain_with_invalid_credentials(self):
        """Test that invalid credentials return 401."""
        response = self.client.post(
            "/api/token/",
            {"email": "test@example.com", "password": "wrongpass"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test refreshing an access token."""
        token_resp = self.client.post(
            "/api/token/",
            {"email": "test@example.com", "password": self.testpass},
            content_type="application/json",
        )
        refresh_token = token_resp.data["refresh"]

        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_unauthenticated_request_fails(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_request_succeeds(self):
        """Test that authenticated requests succeed."""
        self.client.force_login(self.user)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
