"""
Management command to create initial groups (Admin, User) and a default superuser.
Run with: python manage.py create_initial_data
"""

import os
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create initial groups (Admin, User) and a default superuser for development."

    def handle(self, *args, **options):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name="Admin")
        if created:
            self.stdout.write(self.style.SUCCESS("[OK] Created 'Admin' group"))

        user_group, created = Group.objects.get_or_create(name="User")
        if created:
            self.stdout.write(self.style.SUCCESS("[OK] Created 'User' group"))

        # Create default superuser
        superuser_username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        superuser_email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@taskmanager.com")
        superuser_password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Admin@123")

        if not User.objects.filter(username=superuser_username).exists():
            superuser = User.objects.create_superuser(
                username=superuser_username,
                email=superuser_email,
                password=superuser_password,
            )
            superuser.groups.add(admin_group)
            self.stdout.write(
                self.style.SUCCESS(
                    f"[OK] Superuser created: username='{superuser_username}' password='{superuser_password}'"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"[SKIP] Superuser '{superuser_username}' already exists.")
            )

        self.stdout.write(self.style.SUCCESS("\n[DONE] Initial data setup complete!"))
