from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, (DjangoValidationError, DRFValidationError)):
        payload = getattr(exc, "message_dict", None) or getattr(exc, "detail", None) or exc.messages
        response = Response(payload, status=status.HTTP_400_BAD_REQUEST)

    if response is None:
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred",
                "data": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    payload = response.data
    message = "Request failed"

    if isinstance(payload, dict):
        detail = payload.get("detail") or payload.get("message")
        if isinstance(detail, (list, tuple)):
            message = str(detail[0])
        elif detail:
            message = str(detail)
        else:
            first_value = next(iter(payload.values()), None)
            if isinstance(first_value, (list, tuple)) and first_value:
                message = str(first_value[0])
    elif isinstance(payload, (list, tuple)) and payload:
        message = str(payload[0])

    response.data = {
        "success": False,
        "message": message,
        "data": payload,
    }
    return response
