from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Project, ProjectMember


def get_project_and_membership(project_id, user):
    """
    Returns (project, membership).
    Raises NotFound if project doesn't exist, PermissionDenied if user isn't a member.
    """
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise NotFound("Project not found.")

    try:
        membership = ProjectMember.objects.get(project=project, user=user)
    except ProjectMember.DoesNotExist:
        raise PermissionDenied("You are not a member of this project.")

    return project, membership


def require_owner_or_admin(membership):
    if membership.role not in [ProjectMember.Role.OWNER, ProjectMember.Role.ADMIN]:
        raise PermissionDenied("Only an owner or admin can perform this action.")
