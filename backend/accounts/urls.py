"""
URL patterns for the accounts app.
All routes are prefixed with /api/v1/auth/ from the root urls.py.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Authentication
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # User Profile
    path("profile/", views.UserProfileView.as_view(), name="auth-profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="auth-change-password"),

    # Admin User Management
    path("users/", views.AdminUserListView.as_view(), name="admin-user-list"),
    path("users/<int:pk>/", views.AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("users/<int:pk>/promote/", views.AdminPromoteUserView.as_view(), name="admin-promote-user"),
]
