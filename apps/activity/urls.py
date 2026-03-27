from django.urls import path

from .views import (
    ProjectActivityLogView,
    UserActivityLogView,
    ObjectActivityLogView,
)

urlpatterns = [
    # Activity logs
    path("projects/<uuid:project_id>/activity/", ProjectActivityLogView.as_view(), name="project-activity-log"),
    path("activity/", UserActivityLogView.as_view(), name="user-activity-log"),
    path("projects/<uuid:project_id>/activity/<str:content_type>/<uuid:object_id>/", ObjectActivityLogView.as_view(), name="object-activity-log"),
]
