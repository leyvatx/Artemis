import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework.exceptions import APIException
from django.db import connection
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class LoggingMiddleware(MiddlewareMixin):
    """Middleware for logging all requests and responses"""
    
    def process_request(self, request):
        user_info = 'Anonymous'
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = str(request.user)
        except:
            pass
        
        request.log_data = {
            'method': request.method,
            'path': request.path,
            'remote_addr': self.get_client_ip(request),
            'user': user_info,
        }
        return None

    def process_response(self, request, response):
        if hasattr(request, 'log_data'):
            log_data = request.log_data
            log_data['status'] = response.status_code
            
            log_level = logging.DEBUG
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING
            
            logger.log(
                log_level,
                f"{log_data['method']} {log_data['path']} - Status: {log_data['status']} - User: {log_data['user']}"
            )
        
        return response

    def process_exception(self, request, exception):
        """Log unhandled exceptions"""
        user_info = 'Anonymous'
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = str(request.user)
        except:
            pass
        
        logger.error(
            f"Exception in {request.method} {request.path}",
            exc_info=True,
            extra={'user': user_info}
        )
        return None

    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ExceptionHandlerMiddleware(MiddlewareMixin):
    """Middleware for handling and formatting API exceptions"""
    
    def process_exception(self, request, exception):
        """Convert exceptions to JSON responses"""
        
        logger.exception(f"Unhandled exception: {exception}")
        
        if isinstance(exception, ValidationError):
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Validation Error',
                    'message': str(exception),
                    'details': exception.message_dict if hasattr(exception, 'message_dict') else {}
                },
                status=400
            )
        
        if isinstance(exception, APIException):
            return JsonResponse(
                {
                    'success': False,
                    'error': exception.detail,
                    'status_code': exception.status_code
                },
                status=exception.status_code
            )
        
        return JsonResponse(
            {
                'success': False,
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred. Please try again later.'
            },
            status=500
        )
