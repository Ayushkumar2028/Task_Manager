"""
Custom exception handler for consistent API error responses.
All API errors return a structured JSON response with 'success', 'message', and 'errors' keys.
"""

import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that wraps errors in a consistent format:
    {
        "success": false,
        "message": "Error description",
        "errors": { ... }
    }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "message": "An error occurred.",
            "errors": {},
        }

        # Flatten the DRF error data
        if isinstance(response.data, dict):
            # Check for 'detail' key (common in authentication errors)
            if "detail" in response.data:
                error_data["message"] = str(response.data["detail"])
                error_data["errors"] = {}
            else:
                # Field-level validation errors
                error_data["message"] = "Validation failed."
                error_data["errors"] = response.data
        elif isinstance(response.data, list):
            error_data["message"] = str(response.data[0]) if response.data else "Error"
            error_data["errors"] = {}

        # Map status codes to human-readable messages
        status_messages = {
            400: "Bad Request",
            401: "Authentication required. Please provide a valid JWT token.",
            403: "You do not have permission to perform this action.",
            404: "The requested resource was not found.",
            405: "Method not allowed.",
            429: "Too many requests. Please slow down.",
            500: "Internal server error.",
        }

        if not error_data["message"] or error_data["message"] == "An error occurred.":
            error_data["message"] = status_messages.get(
                response.status_code, "An unexpected error occurred."
            )

        # Log the error
        logger.warning(
            f"API Error {response.status_code}: {error_data['message']} | "
            f"View: {context.get('view', 'unknown').__class__.__name__}"
        )

        response.data = error_data

    return response
