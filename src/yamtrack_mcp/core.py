import json
import logging
from datetime import datetime

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.dateparse import parse_date
from mcp.server.fastmcp import FastMCP

from api.serializers.media import (
    MediaSerializer,
    MediaUpdateSerializer,
    ProgressSerializer,
)
from app import statistics as stats
from app.forms import get_form_class
from app.history_processor import process_history_entries
from app.models import BasicMedia, Item, MediaTypes, Status
from app.providers import services
from yamtrack_mcp.auth import get_current_user

logger = logging.getLogger(__name__)

mcp = FastMCP("Yamtrack")


def _user_required():
    user = get_current_user()
    if user is None:
        msg = "Authentication required. Provide a valid JWT token."
        raise ValueError(msg)
    return user


def _get_media_or_error(user, media_type, instance_id):
    try:
        model = apps.get_model("app", media_type)
        return model.objects.select_related("item").get(id=instance_id, user=user)
    except ObjectDoesNotExist:
        msg = f"{media_type} with id {instance_id} not found"
        raise ValueError(msg) from None


@mcp.tool()
def search_media(
    query: str, media_type: str = "tv", page: int = 1, source: str | None = None
) -> str:
    """Search for media across external providers.

    Supported media types: tv, movie, anime, manga, game, book, comic, boardgame.
    """
    results = services.search(media_type, query, page, source)
    return json.dumps(results)


@mcp.tool()
def get_details(
    source: str,
    media_type: str,
    media_id: str,
    season_number: int | None = None,
) -> str:
    """Get metadata details for a media item from an external provider."""
    season_numbers = [season_number] if season_number else None
    metadata = services.get_media_metadata(
        media_type, media_id, source, season_numbers,
    )

    user = get_current_user()
    if user is not None:
        user_media = BasicMedia.objects.filter_media(
            user, media_id, media_type, source, season_number=season_number,
        )
        if user_media.exists():
            metadata["tracking"] = MediaSerializer(user_media.first()).data

    return json.dumps(metadata)


@mcp.tool()
def list_tracked_media(
    media_type: str | None = None,
    status: str = "All",
    sort: str | None = None,
    search: str = "",
) -> str:
    """List media tracked by the authenticated user.

    Status options: All, Completed, In progress, Planning, Paused, Dropped.
    """
    user = _user_required()

    if media_type:
        qs = BasicMedia.objects.get_media_list(user, media_type, status, sort, search)
        serializer = MediaSerializer(qs, many=True)
        return json.dumps({"results": serializer.data, "total": len(serializer.data)})

    grouped = {}
    for mt in MediaTypes.values:
        qs = BasicMedia.objects.get_media_list(user, mt, status, sort, search)
        serializer = MediaSerializer(qs, many=True)
        if serializer.data:
            grouped[mt] = {"results": serializer.data, "total": len(serializer.data)}
    return json.dumps(grouped)


@mcp.tool()
def create_entry(
    media_id: str,
    source: str,
    media_type: str,
    status: str | None = None,
    score: float | None = None,
    progress: int = 0,
    notes: str = "",
) -> str:
    """Start tracking a new media item from an external provider.

    Status defaults to "Completed" if omitted. Score is 0-10.
    """
    user = _user_required()

    metadata = services.get_media_metadata(media_type, media_id, source)

    item, _ = Item.objects.get_or_create(
        media_id=media_id,
        source=source,
        media_type=media_type,
        defaults={"title": metadata["title"], "image": metadata.get("image", "")},
    )

    model = apps.get_model(app_label="app", model_name=media_type)
    instance = model(
        item=item,
        user=user,
        status=status or Status.COMPLETED.value,
        score=score,
        progress=progress,
        notes=notes,
    )

    form_class = get_form_class(media_type)
    if form_class is None:
        return json.dumps({"error": f"No form found for media type '{media_type}'"})

    form = form_class(
        {
            "media_type": media_type,
            "source": source,
            "media_id": media_id,
            "status": instance.status,
            "score": instance.score,
            "progress": instance.progress,
            "notes": instance.notes,
        },
        instance=instance,
    )
    if form.is_valid():
        form.save()
        return json.dumps(MediaSerializer(form.instance).data)

    return json.dumps({"error": form.errors})


@mcp.tool()
def update_entry(
    media_type: str,
    instance_id: int,
    status: str | None = None,
    score: float | None = None,
    progress: int | None = None,
    notes: str | None = None,
) -> str:
    """Update status, score, progress, or notes for a tracked media item."""
    user = _user_required()
    media = _get_media_or_error(user, media_type, instance_id)

    data = {}
    if status is not None:
        data["status"] = status
    if score is not None:
        data["score"] = score
    if progress is not None:
        data["progress"] = progress
    if notes is not None:
        data["notes"] = notes

    serializer = MediaUpdateSerializer(data=data)
    if not serializer.is_valid():
        return json.dumps({"error": serializer.errors})

    for attr, value in serializer.validated_data.items():
        setattr(media, attr, value)
    media.save()
    return json.dumps(MediaSerializer(media).data)


@mcp.tool()
def update_progress(media_type: str, instance_id: int, operation: str) -> str:
    """Increase or decrease progress on a media item.

    Operation must be 'increase' or 'decrease'.
    """
    user = _user_required()
    media = _get_media_or_error(user, media_type, instance_id)

    serializer = ProgressSerializer(data={"operation": operation})
    if not serializer.is_valid():
        return json.dumps({"error": serializer.errors})

    if serializer.validated_data["operation"] == "increase":
        media.increase_progress()
    else:
        media.decrease_progress()

    media.refresh_from_db()
    return json.dumps(MediaSerializer(media).data)


@mcp.tool()
def update_score(media_type: str, instance_id: int, score: float) -> str:
    """Update the score (0-10) for a tracked media item."""
    user = _user_required()
    media = _get_media_or_error(user, media_type, instance_id)

    media.score = score
    media.save()
    return json.dumps(MediaSerializer(media).data)


@mcp.tool()
def get_home(sort: str = "upcoming") -> str:
    """Get dashboard data: in-progress and planning media."""
    user = _user_required()

    in_progress = BasicMedia.objects.get_home_status(
        user=user, status=Status.IN_PROGRESS.value, sort_by=sort,
    )
    planning = BasicMedia.objects.get_home_status(
        user=user, status=Status.PLANNING.value, sort_by=sort,
    )

    def serialize_section(section_data):
        result = {}
        for mt, data in section_data.items():
            serializer = MediaSerializer(data["items"], many=True)
            result[mt] = {"items": serializer.data, "total": data["total"]}
        return result

    return json.dumps({
        "in_progress": serialize_section(in_progress),
        "planning": serialize_section(planning),
    })


@mcp.tool()
def get_statistics(
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get aggregated statistics for the authenticated user.

    Dates in YYYY-MM-DD format. Use 'all'/'all' for no filter.
    Defaults to last 365 days.
    """
    user = _user_required()

    today = timezone.localdate()

    if start_date == "all" and end_date == "all":
        start = None
        end = None
    else:
        if start_date:
            start = parse_date(start_date)
        else:
            start = today.replace(year=today.year - 1)
        end = parse_date(end_date) if end_date else today
        if start and end:
            start = timezone.make_aware(datetime.combine(start, datetime.min.time()))
            end = timezone.make_aware(datetime.combine(end, datetime.max.time()))

    user_media, media_count = stats.get_user_media(user, start, end)
    return json.dumps({
        "media_count": media_count,
        "media_type_distribution": stats.get_media_type_distribution(media_count),
        "score_distribution": stats.get_score_distribution(user_media)[0],
        "top_rated": stats.get_score_distribution(user_media)[1],
        "status_distribution": stats.get_status_distribution(user_media),
        "timeline": stats.get_timeline(user_media),
        "activity_data": stats.get_activity_data(user, start, end),
    })


@mcp.tool()
def get_history(
    source: str,
    media_type: str,
    media_id: str,
    season_number: int | None = None,
    episode_number: int | None = None,
) -> str:
    """Get change history for a tracked media item."""
    user = _user_required()

    user_medias = BasicMedia.objects.filter_media(
        user,
        media_id,
        media_type,
        source,
        season_number=season_number,
        episode_number=episode_number,
    )

    total = user_medias.count()
    timeline = []
    for index, media in enumerate(user_medias, start=1):
        if history := media.history.all():
            entry_number = total - index + 1
            timeline.extend(
                process_history_entries(history, media_type, entry_number, user),
            )

    return json.dumps({"timeline": timeline, "total": total})
