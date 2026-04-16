"""
Custom DRF permissions for role-based access control.
"""

from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Grants access only to users in the 'Admin' group or Django superusers.
    """

    message = "You must be an admin to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.groups.filter(name="Admin").exists()


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allows access if user owns the object, or is an admin.
    The object must have a 'user' attribute.
    """

    message = "You can only access your own resources."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admins and superusers bypass ownership check
        if request.user.is_superuser or request.user.groups.filter(name="Admin").exists():
            return True
        # Regular users can only access their own objects
        return obj.user == request.user
