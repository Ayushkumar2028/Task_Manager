"""
Task serializers with full validation and nested user info.
"""

from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Full Task serializer for create/update/read operations.
    - 'user' is read-only and auto-set from the request context
    - Includes computed fields: owner_username, is_overdue
    """

    owner_username = serializers.CharField(source="user.username", read_only=True)
    owner_email = serializers.CharField(source="user.email", read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "user",
            "owner_username",
            "owner_email",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "owner_username", "owner_email", "created_at", "updated_at"]

    def get_is_overdue(self, obj):
        """Task is overdue if there's a past due date and it's not completed."""
        from django.utils import timezone
        if obj.due_date and obj.status not in ["completed", "cancelled"]:
            return obj.due_date < timezone.now().date()
        return False

    def validate_title(self, value):
        """Ensure title is not just whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or only whitespace.")
        return value.strip()

    def validate_due_date(self, value):
        """Ensure due_date is not in the past when creating (allow on update)."""
        from django.utils import timezone
        # Only validate on creation (no instance exists yet)
        if value and self.instance is None and value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def create(self, validated_data):
        """Auto-assign the current user as task owner. Admins can assign to others."""
        request = self.context["request"]
        user_id = request.data.get("user")
        
        is_admin = request.user.is_superuser or request.user.groups.filter(name="Admin").exists()
        
        if is_admin and user_id:
            from django.contrib.auth.models import User
            try:
                assigned_user = User.objects.get(id=user_id)
                validated_data["user"] = assigned_user
            except User.DoesNotExist:
                validated_data["user"] = request.user
        else:
            validated_data["user"] = request.user
            
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing tasks (fewer fields for performance).
    """

    owner_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "status", "priority", "due_date",
            "owner_username", "created_at", "updated_at",
        ]
