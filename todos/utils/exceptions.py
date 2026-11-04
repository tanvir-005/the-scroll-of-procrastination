from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if isinstance(response.data, dict):
        errors = response.data
    else:
        errors = {"detail": response.data}

    status_messages = {
        400: "Validation failed.",
        401: "Authentication required.",
        403: "Permission denied.",
        404: "Resource not found.",
    }

    response.data = {
        "success": False,
        "message": status_messages.get(
            response.status_code,
            "Request failed."
        ),
        "errors": errors
    }

    return response