from rest_framework import serializers

from .models import Invitation, Project, ProjectMember


class ProjectSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name", "description", "project_type", "owner",
            "currency", "budget", "start_date", "end_date",
            "is_active", "is_archived", "member_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "is_archived", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.members.count()

    def validate_budget(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Budget must be a positive number.")
        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date") or (self.instance and self.instance.start_date)
        end_date = attrs.get("end_date") or (self.instance and self.instance.end_date)
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "end_date must be after start_date."})
        return attrs


class ProjectMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            "id", "user", "email", "first_name", "last_name", "role",
            "can_create_transactions", "can_edit_transactions",
            "can_delete_transactions", "can_view_reports", "can_invite_members",
            "joined_at",
        ]
        read_only_fields = ["id", "user", "email", "first_name", "last_name", "joined_at"]


class InvitationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id", "project", "project_name", "email", "role",
            "invited_by", "invited_by_email", "status", "created_at", "expires_at",
        ]
        read_only_fields = [
            "id", "project", "invited_by", "status", "created_at", "expires_at",
        ]


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=ProjectMember.Role.choices, default=ProjectMember.Role.MEMBER
    )
