from django.utils.deprecation import MiddlewareMixin


class ArtemisMiddleware(MiddlewareMixin):
    """Custom middleware for Artemis."""

    def process_request(self, request):
        # Add custom logic here
        pass

    def process_response(self, request, response):
        # Add custom logic here
        return response