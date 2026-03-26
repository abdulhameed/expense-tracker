from django.urls import path

from .views import (
    AcceptInvitationView,
    DeclineInvitationView,
    InvitationListView,
    InviteMemberView,
    LeaveProjectView,
    ProjectArchiveView,
    ProjectDetailView,
    ProjectListCreateView,
    ProjectMemberDetailView,
    ProjectMemberListView,
    ProjectStatsView,
)

urlpatterns = [
    # Projects
    path("projects/", ProjectListCreateView.as_view(), name="project-list"),
    path("projects/<uuid:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/<uuid:pk>/archive/", ProjectArchiveView.as_view(), name="project-archive"),
    path("projects/<uuid:pk>/stats/", ProjectStatsView.as_view(), name="project-stats"),
    # Members
    path("projects/<uuid:pk>/members/", ProjectMemberListView.as_view(), name="project-member-list"),
    path("projects/<uuid:pk>/members/invite/", InviteMemberView.as_view(), name="project-member-invite"),
    path("projects/<uuid:pk>/members/leave/", LeaveProjectView.as_view(), name="project-member-leave"),
    path(
        "projects/<uuid:pk>/members/<uuid:member_id>/",
        ProjectMemberDetailView.as_view(),
        name="project-member-detail",
    ),
    # Invitations
    path("invitations/", InvitationListView.as_view(), name="invitation-list"),
    path("invitations/<str:token>/accept/", AcceptInvitationView.as_view(), name="invitation-accept"),
    path("invitations/<str:token>/decline/", DeclineInvitationView.as_view(), name="invitation-decline"),
]
