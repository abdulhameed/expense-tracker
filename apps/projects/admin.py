from django.contrib import admin

from .models import Invitation, Project, ProjectMember


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "project_type", "owner", "currency", "is_active", "is_archived", "created_at"]
    list_filter = ["project_type", "is_active", "is_archived"]
    search_fields = ["name", "owner__email"]
    raw_id_fields = ["owner"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "role", "joined_at"]
    list_filter = ["role"]
    raw_id_fields = ["project", "user", "invited_by"]
    readonly_fields = ["joined_at"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "project", "role", "status", "invited_by", "created_at", "expires_at"]
    list_filter = ["status", "role"]
    raw_id_fields = ["project", "invited_by"]
    readonly_fields = ["created_at", "token"]
