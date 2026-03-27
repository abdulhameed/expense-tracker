from rest_framework import serializers

from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_currency = serializers.CharField(source="project.currency", read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id",
            "project",
            "project_name",
            "project_currency",
            "category",
            "category_name",
            "amount",
            "period",
            "start_date",
            "end_date",
            "alert_threshold",
            "alert_enabled",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        """Validate budget data."""
        request = self.context.get("request")
        project = attrs.get("project") or (self.instance and self.instance.project)

        # Validate permission
        if project and request:
            from apps.projects.models import ProjectMember

            is_member = ProjectMember.objects.filter(
                project=project,
                user=request.user,
                role__in=[ProjectMember.Role.OWNER, ProjectMember.Role.ADMIN],
            ).exists()
            if not is_member:
                raise serializers.ValidationError(
                    "You do not have permission to manage budgets for this project."
                )

        # Validate dates
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Start date must be before end date."
            )

        # Validate amount
        amount = attrs.get("amount")
        if amount and amount <= 0:
            raise serializers.ValidationError(
                "Budget amount must be greater than zero."
            )

        # Validate alert threshold
        alert_threshold = attrs.get("alert_threshold")
        if alert_threshold is not None:
            if alert_threshold < 0 or alert_threshold > 100:
                raise serializers.ValidationError(
                    "Alert threshold must be between 0 and 100."
                )

        return attrs


class BudgetStatusSerializer(serializers.Serializer):
    """Serializer for budget status information."""

    budget_id = serializers.UUIDField()
    allocated = serializers.DecimalField(max_digits=15, decimal_places=2)
    spent = serializers.DecimalField(max_digits=15, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=15, decimal_places=2)
    percentage_used = serializers.FloatField()
    alert_triggered = serializers.BooleanField()
    period = serializers.CharField()
    category_name = serializers.CharField(required=False, allow_null=True)
