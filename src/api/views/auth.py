"""Authentication views for the API."""

from django.contrib.auth.decorators import login_not_required
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.auth import UserSerializer


@login_not_required
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    """Get or update the current user's profile."""
    if request.method == "GET":
        return Response(UserSerializer(request.user).data)

    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
