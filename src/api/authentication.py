"""JWT authentication using email instead of username."""

from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class UsernameTokenObtainSerializer(TokenObtainPairSerializer):
    """Token serializer that authenticates by username."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)
        self.fields["username"] = serializers.CharField()
        self.fields.pop("email", None)

    def validate(self, attrs):
        """Authenticate by username and return JWT tokens."""
        username = attrs.get("username")
        password = attrs.get("password")
        user = get_user_model().objects.filter(username=username).first()
        if not user or not user.check_password(password):
            msg = "No active account found with these credentials"
            raise exceptions.AuthenticationFailed(msg)
        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class UsernameTokenObtainPairView(TokenObtainPairView):
    """View for obtaining JWT tokens using username authentication."""

    serializer_class = UsernameTokenObtainSerializer
