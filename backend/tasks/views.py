"""
Task views — complete CRUD with RBAC enforcement.
- Regular users see and manage only their own tasks
- Admins see and manage all tasks
"""

import logging

from django.db.models import Q
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.permissions import IsAdminUser, IsOwnerOrAdmin
from .models import Task
from .serializers import TaskSerializer, TaskListSerializer

logger = logging.getLogger(__name__)


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """Helper for consistent success JSON responses."""
    return Response(
        {"success": True, "message": message, "data": data},
        status=status_code,
    )


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/tasks/       — List tasks (filtered by user; admin sees all)
    POST /api/v1/tasks/       — Create a new task (auto-assigned to current user)

    Supports query params:
        ?status=pending|in_progress|completed|cancelled
        ?priority=low|medium|high|urgent
        ?search=<term>         (searches title and description)
        ?ordering=created_at|-created_at|due_date|priority
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Admins see ALL tasks. Regular users only see their own.
        Supports filtering by status and priority.
        """
        user = self.request.user
        is_admin = user.is_superuser or user.groups.filter(name="Admin").exists()

        # Base queryset
        if is_admin:
            queryset = Task.objects.all().select_related("user")
        else:
            queryset = Task.objects.filter(user=user).select_related("user")

        # Optional filters
        status_filter = self.request.query_params.get("status")
        priority_filter = self.request.query_params.get("priority")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        return queryset

    def get_serializer_class(self):
        """Use lightweight serializer for lists, full serializer for detail."""
        if self.request.method == "GET":
            return TaskListSerializer
        return TaskSerializer

    @swagger_auto_schema(
        operation_summary="List tasks",
        operation_description="Returns tasks for the current user. Admins see all tasks.",
        manual_parameters=[
            openapi.Parameter("status", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=["pending", "in_progress", "completed", "cancelled"]),
            openapi.Parameter("priority", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=["low", "medium", "high", "urgent"]),
            openapi.Parameter("search", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data={"count": queryset.count(), "tasks": serializer.data},
            message=f"{queryset.count()} task(s) found.",
        )

    @swagger_auto_schema(
        operation_summary="Create a new task",
        request_body=TaskSerializer,
        responses={201: TaskSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        logger.info(f"Task created: '{task.title}' by {request.user.username}")
        return success_response(
            data=serializer.data,
            message="Task created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/tasks/<id>/   — Retrieve task details
    PUT    /api/v1/tasks/<id>/   — Full update
    PATCH  /api/v1/tasks/<id>/   — Partial update
    DELETE /api/v1/tasks/<id>/   — Delete task

    Object-level permission: users can only access their own tasks.
    Admins can access any task.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Admin").exists():
            return Task.objects.all().select_related("user")
        return Task.objects.filter(user=user).select_related("user")

    @swagger_auto_schema(operation_summary="Get task detail")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    @swagger_auto_schema(operation_summary="Update task (full)")
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        logger.info(f"Task updated: '{task.title}' by {request.user.username}")
        return success_response(data=serializer.data, message="Task updated successfully.")

    @swagger_auto_schema(operation_summary="Delete task")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        instance.delete()
        logger.info(f"Task deleted: '{title}' by {request.user.username}")
        return success_response(message=f"Task '{title}' deleted successfully.")


class TaskStatsView(APIView):
    """
    GET /api/v1/tasks/stats/
    Returns task statistics for the current user (or all tasks for admin).
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get task statistics")
    def get(self, request):
        user = request.user
        is_admin = user.is_superuser or user.groups.filter(name="Admin").exists()

        queryset = Task.objects.all() if is_admin else Task.objects.filter(user=user)

        stats = {
            "total": queryset.count(),
            "by_status": {
                "pending": queryset.filter(status=Task.Status.PENDING).count(),
                "in_progress": queryset.filter(status=Task.Status.IN_PROGRESS).count(),
                "completed": queryset.filter(status=Task.Status.COMPLETED).count(),
                "cancelled": queryset.filter(status=Task.Status.CANCELLED).count(),
            },
            "by_priority": {
                "low": queryset.filter(priority=Task.Priority.LOW).count(),
                "medium": queryset.filter(priority=Task.Priority.MEDIUM).count(),
                "high": queryset.filter(priority=Task.Priority.HIGH).count(),
                "urgent": queryset.filter(priority=Task.Priority.URGENT).count(),
            },
        }

        return success_response(data=stats, message="Task statistics retrieved.")
