"""JWT authentication using email instead of username."""

from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class EmailTokenObtainSerializer(TokenObtainPairSerializer):
    """Token serializer that authenticates by email."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField()
        self.fields.pop("username", None)

    def validate(self, attrs):
        """Authenticate by email and return JWT tokens."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = get_user_model().objects.filter(email=email).first()
        if not user or not user.check_password(password):
            msg = "No active account found with these credentials"
            raise exceptions.AuthenticationFailed(msg)
        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class EmailTokenObtainPairView(TokenObtainPairView):
    """View for obtaining JWT tokens using email authentication."""

    serializer_class = EmailTokenObtainSerializer
