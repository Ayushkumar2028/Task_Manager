"""
Accounts serializers for user registration, profile, and JWT customization.
"""

import logging

from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    - Validates password strength using Django's built-in validators
    - Automatically assigns the 'User' role group on creation
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password",
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "password2"]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value):
        """Ensure email is unique across all users."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        """Ensure both passwords match."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """Create user with hashed password and assign 'User' group."""
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # create_user uses Django's built-in password hashing (PBKDF2)
        user = User.objects.create_user(password=password, **validated_data)

        # Assign default 'User' group (create if not exists)
        user_group, _ = Group.objects.get_or_create(name="User")
        user.groups.add(user_group)

        logger.info(f"New user registered: {user.username} (id={user.id})")
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/updating user profile information.
    Includes role information derived from group membership.
    """

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "date_joined", "last_login"]
        read_only_fields = ["id", "username", "date_joined", "last_login", "role"]

    def get_role(self, obj):
        """Return the user's primary role based on their group membership."""
        groups = obj.groups.values_list("name", flat=True)
        if obj.is_superuser or "Admin" in groups:
            return "Admin"
        return "User"


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing a user's password."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that adds user info to the token claims.
    Also returns user profile data alongside the tokens.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the JWT payload
        token["username"] = user.username
        token["email"] = user.email
        token["is_admin"] = user.is_superuser or user.groups.filter(name="Admin").exists()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Append user profile data to the login response
        user = self.user
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": "Admin" if (user.is_superuser or user.groups.filter(name="Admin").exists()) else "User",
        }

        logger.info(f"User logged in: {user.username}")
        return data
