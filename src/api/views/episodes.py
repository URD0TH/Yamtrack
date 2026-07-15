"""Episode tracking views for the API."""

import logging

from django.contrib.auth.decorators import login_not_required
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.serializers.media import EpisodeCreateSerializer
from app.models import (
    Episode,
    Item,
    MediaTypes,
    Season,
    Sources,
    Status,
)
from app.providers import services

logger = logging.getLogger(__name__)


@login_not_required
@api_view(["POST"])
def episode_create(request):
    """Create a watched episode entry."""
    serializer = EpisodeCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        related_season = Season.objects.get(
            item__media_id=data["media_id"],
            item__source=data["source"],
            item__season_number=data["season_number"],
            item__episode_number=None,
            user=request.user,
        )
    except Season.DoesNotExist:
        tv_with_seasons = services.get_media_metadata(
            "tv_with_seasons",
            data["media_id"],
            data["source"],
            [data["season_number"]],
        )
        season_metadata = tv_with_seasons[f"season/{data['season_number']}"]
        item, _ = Item.objects.get_or_create(
            media_id=data["media_id"],
            source=Sources.TMDB.value,
            media_type=MediaTypes.SEASON.value,
            season_number=data["season_number"],
            defaults={
                "title": tv_with_seasons["title"],
                "image": season_metadata["image"],
            },
        )
        related_season = Season.objects.create(
            item=item,
            user=request.user,
            score=None,
            status=Status.IN_PROGRESS.value,
            notes="",
        )
        logger.info("%s did not exist, it was created successfully.", related_season)

    end_date = data.get("end_date") or timezone.now().replace(second=0, microsecond=0)
    episode = (
        Episode.objects.filter(
            related_season=related_season,
            item__episode_number=data["episode_number"],
        )
        .order_by("-end_date")
        .first()
    )
    if episode is None:
        related_season.watch(data["episode_number"], end_date)
        return Response(status=status.HTTP_201_CREATED)

    episode.end_date = end_date
    episode.save()
    return Response(status=status.HTTP_200_OK)
