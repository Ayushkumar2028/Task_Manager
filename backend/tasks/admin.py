"""
Django Admin configuration for the tasks app.
Provides a rich, filterable interface for managing tasks.
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin panel configuration for Task model."""

    list_display = (
        "id", "title", "user", "status", "priority",
        "due_date", "created_at", "updated_at",
    )
    list_filter = ("status", "priority", "created_at", "due_date")
    search_fields = ("title", "description", "user__username", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25

    fieldsets = (
        ("Task Information", {
            "fields": ("title", "description", "user"),
        }),
        ("Status & Priority", {
            "fields": ("status", "priority", "due_date"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related for user field."""
        return super().get_queryset(request).select_related("user")
