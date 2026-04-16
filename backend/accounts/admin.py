"""
Django Admin configuration for the accounts app.
Customizes the User admin to show group/role information clearly.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group


class CustomUserAdmin(UserAdmin):
    """Extended User admin with role display."""

    list_display = (
        "username", "email", "first_name", "last_name",
        "get_role", "is_staff", "is_active", "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    def get_role(self, obj):
        """Display the user's role group."""
        groups = obj.groups.values_list("name", flat=True)
        if obj.is_superuser:
            return "⭐ Superuser"
        elif "Admin" in groups:
            return "🔑 Admin"
        return "👤 User"

    get_role.short_description = "Role"
    get_role.admin_order_field = "groups"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
