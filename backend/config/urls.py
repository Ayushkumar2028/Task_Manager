"""
Root URL configuration for the TaskManager project.
API versioning is implemented via /api/v1/ prefix.
Swagger UI is available at /swagger/ and ReDoc at /redoc/.
"""

from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# ==============================================================================
# SWAGGER / OPENAPI SCHEMA CONFIGURATION
# ==============================================================================
api_info = openapi.Info(
    title="TaskManager API",
    default_version="v1",
    description="""
    ## TaskManager REST API

    A full-featured task management API with JWT authentication and role-based access control.

    ### Authentication
    Use JWT Bearer tokens. Obtain a token via `/api/v1/auth/login/`.
    Include the token in the `Authorization` header: `Bearer <your_token>`

    ### Roles
    - **Admin**: Full access to all resources (users, tasks)
    - **User**: Can only manage their own tasks

    ### API Versioning
    All endpoints are prefixed with `/api/v1/`
    """,
    terms_of_service="https://www.example.com/terms/",
    contact=openapi.Contact(email="admin@taskmanager.com"),
    license=openapi.License(name="MIT License"),
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=[permissions.AllowAny],
)

# ==============================================================================
# URL PATTERNS
# ==============================================================================
urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # API v1 Routes
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/tasks/", include("tasks.urls")),

    # Swagger UI
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # DRF Browsable API Auth
    path("api-auth/", include("rest_framework.urls")),
]

# Custom Admin Site Configuration
admin.site.site_header = "TaskManager Administration"
admin.site.site_title = "TaskManager Admin"
admin.site.index_title = "Welcome to TaskManager Admin Panel"
