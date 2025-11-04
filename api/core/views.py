from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet with standard CRUD operations
    """
    
    def create(self, request, *args, **kwargs):
        """Create a new instance with custom response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'success': True, 'data': serializer.data, 'message': 'Created successfully'},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        """Update an instance with custom response"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {'success': True, 'data': serializer.data, 'message': 'Updated successfully'},
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete an instance with custom response"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'success': True, 'message': 'Deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    def list(self, request, *args, **kwargs):
        """List all instances"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single instance"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
