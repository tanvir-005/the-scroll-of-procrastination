from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(response.data, dict):
        errors = response.data
    else:
        errors = {"detail": response.data}

    message = "Request failed."

    if response.status_code == 400:
        message = "Validation failed."
    elif response.status_code == 401:
        message = "Authentication required."
    elif response.status_code == 403:
        message = "Permission denied."
    elif response.status_code == 404:
        message = "Resource not found."
    elif response.status_code >= 500:
        message = "Internal server error."

    response.data = {
        "success": False,
        "message": message,
        "errors": errors
    }

    return response