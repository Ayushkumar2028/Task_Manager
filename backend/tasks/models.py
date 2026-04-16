"""
Task model — the core CRUD entity of the application.
Each task is owned by a User (ForeignKey).
"""

from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    """
    Represents a task owned by a user.

    Fields:
        title       — Short title of the task (required)
        description — Detailed description (optional)
        status      — Current state of the task
        priority    — Task priority level
        due_date    — Optional deadline
        user        — Owner of the task (ForeignKey to auth.User)
        created_at  — Auto-set on creation
        updated_at  — Auto-updated on save
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=255, help_text="Brief title of the task")
    description = models.TextField(blank=True, default="", help_text="Detailed task description")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
    )
    due_date = models.DateField(null=True, blank=True, help_text="Optional task deadline")

    # Ownership — cascade delete when user is deleted
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="The user who owns this task",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "priority"]),
        ]

    def __str__(self):
        return f"[{self.status.upper()}] {self.title} — {self.user.username}"
