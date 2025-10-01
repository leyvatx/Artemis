from rest_framework.exceptions import APIException


class ArtemisException(APIException):
    """Base exception for Artemis API errors."""
    pass


class ValidationError(ArtemisException):
    status_code = 400
    default_detail = 'Invalid input data.'


class NotFoundError(ArtemisException):
    status_code = 404
    default_detail = 'Resource not found.'


class PermissionDeniedError(ArtemisException):
    status_code = 403
    default_detail = 'Permission denied.'