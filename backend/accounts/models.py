"""
Accounts app models.
Uses Django's built-in User model — no custom model needed.
Roles are managed via Django Groups (Admin, User).
"""

# We rely entirely on Django's contrib.auth User model.
# Group-based role management is configured in the admin and via signals.
