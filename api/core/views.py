from rest_framework import viewsets


class BaseViewSet(viewsets.ModelViewSet):
    """Base viewset that disables PATCH and centralizes allowed methods.

    Subclass this in application viewsets to avoid repeating http_method_names.
    """
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']
