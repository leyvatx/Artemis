from rest_framework.exceptions import APIException
from rest_framework import status


class ArtemisAPIException(APIException):
    """Base exception for Artemis API"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred in the Artemis API.'
    default_code = 'error'


class ValidationException(ArtemisAPIException):
    """Validation error exception"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input data.'
    default_code = 'validation_error'


class ResourceNotFoundException(ArtemisAPIException):
    """Resource not found exception"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'


class UnauthorizedException(ArtemisAPIException):
    """Unauthorized access exception"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials are required.'
    default_code = 'unauthorized'


class ForbiddenException(ArtemisAPIException):
    """Forbidden access exception"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to access this resource.'
    default_code = 'forbidden'


class ConflictException(ArtemisAPIException):
    """Conflict exception (e.g., duplicate resource)"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'The resource already exists or conflicts with existing data.'
    default_code = 'conflict'


class ServiceUnavailableException(ArtemisAPIException):
    """Service unavailable exception"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'The service is temporarily unavailable.'
    default_code = 'service_unavailable'
