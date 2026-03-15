from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message="Request successful", status_code=status.HTTP_200_OK, headers=None):
    response = Response(data=data, status=status_code, headers=headers)
    response._message = message
    return response


def error_response(data=None, message="Request failed", status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "success": False,
            "message": message,
            "data": data,
        },
        status=status_code,
    )
