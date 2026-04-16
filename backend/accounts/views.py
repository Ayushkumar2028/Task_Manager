"""
Accounts views — Registration, Profile, Password Change, and Admin User Management.
All responses follow a consistent { success, message, data } structure.
"""

import logging

from django.contrib.auth.models import User, Group
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .permissions import IsAdminUser
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)

logger = logging.getLogger(__name__)


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """Helper to build a consistent success response."""
    return Response(
        {"success": True, "message": message, "data": data},
        status=status_code,
    )


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Register a new user account. No authentication required.
    Password is hashed using Django's PBKDF2 algorithm.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Create a new user account. The password is securely hashed.",
        responses={
            201: openapi.Response("User created successfully"),
            400: openapi.Response("Validation error"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(
            data=UserProfileSerializer(user).data,
            message="Account created successfully. Please log in.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Authenticate and receive JWT access + refresh tokens.
    Also returns the user's profile data.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Login and obtain JWT tokens",
        operation_description="Provide username and password to receive access and refresh JWT tokens.",
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "data": response.data,
                },
                status=status.HTTP_200_OK,
            )
        return response


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklist the refresh token to invalidate the session.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout (blacklist refresh token)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)},
            required=["refresh"],
        ),
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"success": False, "message": "Refresh token is required.", "errors": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User logged out: {request.user.username}")
            return success_response(message="Successfully logged out.")
        except Exception as e:
            logger.warning(f"Logout error: {str(e)}")
            return Response(
                {"success": False, "message": "Invalid token.", "errors": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/auth/profile/   — Retrieve the authenticated user's profile.
    PUT  /api/v1/auth/profile/   — Update name/email fields.
    PATCH /api/v1/auth/profile/  — Partial update.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(operation_summary="Get current user profile")
    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data, message="Profile retrieved.")

    @swagger_auto_schema(operation_summary="Update user profile")
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Profile updated successfully.")


class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password/
    Change the authenticated user's password.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change password",
        request_body=ChangePasswordSerializer,
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        logger.info(f"Password changed for user: {request.user.username}")
        return success_response(message="Password changed successfully.")


# ==============================================================================
# ADMIN-ONLY USER MANAGEMENT VIEWS
# ==============================================================================

class AdminUserListView(generics.ListAPIView):
    """
    GET /api/v1/auth/users/
    Admin-only: List all registered users with their roles.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return User.objects.all().order_by("-date_joined").prefetch_related("groups")

    @swagger_auto_schema(operation_summary="[Admin] List all users")
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message=f"{queryset.count()} users found.")


class AdminUserDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/v1/auth/users/<id>/   — Admin: Retrieve a specific user.
    DELETE /api/v1/auth/users/<id>/   — Admin: Delete a specific user.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()

    @swagger_auto_schema(operation_summary="[Admin] Get user detail")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    @swagger_auto_schema(operation_summary="[Admin] Delete a user")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username
        instance.delete()
        logger.info(f"Admin {request.user.username} deleted user: {username}")
        return success_response(message=f"User '{username}' deleted successfully.")


class AdminPromoteUserView(APIView):
    """
    POST /api/v1/auth/users/<id>/promote/
    Admin-only: Assign the 'Admin' group to a user.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(operation_summary="[Admin] Promote user to Admin role")
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found.", "errors": {}},
                status=status.HTTP_404_NOT_FOUND,
            )
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        user.groups.add(admin_group)
        logger.info(f"Admin {request.user.username} promoted user {user.username} to Admin.")
        return success_response(message=f"User '{user.username}' has been promoted to Admin.")
