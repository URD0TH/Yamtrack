from django.urls import path

from api.views import auth, episodes, history, media, search, statistics

urlpatterns = [
    path("token/", auth.CustomTokenObtainPairView.as_view(), name="api_token_obtain"),
    path(
        "token/refresh/",
        auth.CustomTokenRefreshView.as_view(),
        name="api_token_refresh",
    ),
    path("auth/me/", auth.me, name="api_auth_me"),
    path("search/", search.search, name="api_search"),
    path("home/", media.home, name="api_home"),
    path(
        "details/<str:source>/<str:media_type>/<str:media_id>/",
        media.details,
        name="api_details",
    ),
    path(
        "details/<str:source>/tv/<str:media_id>/season/<int:season_number>/",
        media.season_details,
        name="api_season_details",
    ),
    path("media/<str:media_type>/", media.media_list, name="api_media_list"),
    path("media/manual/create/", media.create_entry, name="api_create_entry"),
    path("media/<str:media_type>/create/", media.media_create, name="api_media_create"),
    path(
        "media/<str:media_type>/<int:instance_id>/",
        media.media_update,
        name="api_media_update",
    ),
    path(
        "media/<str:media_type>/<int:instance_id>/delete/",
        media.media_delete,
        name="api_media_delete",
    ),
    path(
        "media/<str:media_type>/<int:instance_id>/progress/",
        media.progress_edit,
        name="api_progress_edit",
    ),
    path(
        "media/<str:media_type>/<int:instance_id>/score/",
        media.update_score,
        name="api_update_score",
    ),
    path(
        "sync/<str:source>/<str:media_type>/<str:media_id>/",
        media.sync_metadata,
        name="api_sync_metadata",
    ),
    path("episodes/", episodes.episode_create, name="api_episode_create"),
    path(
        "history/<str:media_type>/<int:history_id>/delete/",
        history.history_delete,
        name="api_history_delete",
    ),
    path(
        "history/<str:source>/<str:media_type>/<str:media_id>/",
        history.history_list,
        name="api_history_list",
    ),
    path("statistics/", statistics.statistics, name="api_statistics"),
]
