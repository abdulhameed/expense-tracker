from rest_framework import serializers

from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "category_type",
            "icon",
            "color",
            "project",
            "is_default",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "is_default"]

    def validate(self, attrs):
        request = self.context["request"]
        project = attrs.get("project") or (self.instance and self.instance.project)

        if project and project.owner != request.user:
            from apps.projects.models import ProjectMember

            is_member = ProjectMember.objects.filter(
                project=project,
                user=request.user,
                role__in=[ProjectMember.Role.OWNER, ProjectMember.Role.ADMIN],
            ).exists()
            if not is_member:
                raise serializers.ValidationError(
                    "You do not have permission to manage categories for this project."
                )
        return attrs


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "project",
            "category",
            "category_name",
            "created_by",
            "created_by_email",
            "transaction_type",
            "amount",
            "currency",
            "description",
            "notes",
            "date",
            "payment_method",
            "reference_number",
            "tags",
            "is_recurring",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "project", "created_by", "created_at", "updated_at"]


class TransactionBulkSerializer(serializers.Serializer):
    transactions = TransactionSerializer(many=True)

    def validate_transactions(self, value):
        if not value:
            raise serializers.ValidationError("At least one transaction is required.")
        if len(value) > 100:
            raise serializers.ValidationError("Cannot bulk create more than 100 transactions at once.")
        return value
