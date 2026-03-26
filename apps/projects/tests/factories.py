from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.authentication.tests.factories import UserFactory
from apps.projects.models import Invitation, Project, ProjectMember


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker("text", max_nb_chars=200)
    project_type = Project.ProjectType.PERSONAL
    owner = factory.SubFactory(UserFactory)
    currency = "USD"
    is_active = True
    is_archived = False

    @factory.post_generation
    def add_owner_member(obj, create, extracted, **kwargs):
        """Auto-creates the owner as a ProjectMember unless suppressed."""
        if create and extracted is not False:
            ProjectMember.objects.get_or_create(
                project=obj,
                user=obj.owner,
                defaults={"role": ProjectMember.Role.OWNER},
            )


class ProjectMemberFactory(DjangoModelFactory):
    class Meta:
        model = ProjectMember

    project = factory.SubFactory(ProjectFactory, add_owner_member=False)
    user = factory.SubFactory(UserFactory)
    role = ProjectMember.Role.MEMBER


class InvitationFactory(DjangoModelFactory):
    class Meta:
        model = Invitation

    project = factory.SubFactory(ProjectFactory)
    email = factory.Faker("email")
    role = ProjectMember.Role.MEMBER
    invited_by = factory.SubFactory(UserFactory)
    status = Invitation.Status.PENDING
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
