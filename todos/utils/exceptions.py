from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "error": "Internal server error.",
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    status_messages = {
        400: "Validation failed.",
        401: "Authentication required.",
        403: "Permission denied.",
        404: "Resource not found.",
        405: "Method not allowed.",
        429: "Too many requests.",
    }

    response.data = {
        "error": status_messages.get(
            response.status_code,
            "Request failed."
        ),
        "code": response.status_code
    }

    return response