"""User serializers for the API."""

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        """Meta options for UserSerializer."""

        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile_private",
            "token",
            "release_notifications_enabled",
            "daily_digest_enabled",
            "notification_urls",
        ]
        read_only_fields = ["id", "token"]
