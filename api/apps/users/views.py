from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.views import BaseViewSet
from .models import Role, User, SupervisorAssignment
from .serializers import (
    RoleSerializer, UserSerializer, SupervisorAssignmentSerializer, 
    UserDetailSerializer, OfficerSerializer, SupervisorSerializer,
    CleanSupervisorAssignmentSerializer
)


class RoleViewSet(BaseViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'], url_path='supervisors')
    def list_supervisors(self, request):
        """
        Obtener lista de todos los supervisores.
        GET /users/supervisors/
        """
        supervisors = User.objects.filter(
            supervisor_assignments__isnull=False
        ).distinct()
        
        serializer = SupervisorSerializer(supervisors, many=True)
        return Response({
            'success': True,
            'count': supervisors.count(),
            'supervisors': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='officers')
    def list_officers(self, request):
        """
        Obtener lista de todos los oficiales.
        GET /users/officers/
        """
        officers = User.objects.filter(
            officer_assignments__isnull=False
        ).distinct()
        
        serializer = OfficerSerializer(officers, many=True)
        return Response({
            'success': True,
            'count': officers.count(),
            'officers': serializer.data
        }, status=status.HTTP_200_OK)


class SupervisorAssignmentViewSet(BaseViewSet):
    queryset = SupervisorAssignment.objects.all()
    serializer_class = SupervisorAssignmentSerializer
    
    def get_serializer_class(self):
        """Usar serializer limpio para list y retrieve"""
        if self.action in ['list', 'retrieve']:
            return CleanSupervisorAssignmentSerializer
        return SupervisorAssignmentSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list para usar serializer limpio y formato personalizado"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'assignments': serializer.data
        }, status=status.HTTP_200_OK)


class SupervisorViewSet(viewsets.ViewSet):
    """ViewSet para gestionar supervisores y sus oficiales"""
    
    @action(detail=True, methods=['get'], url_path='officers')
    def get_officers(self, request, pk=None):
        """
        Obtener todos los oficiales a cargo de un supervisor específico.
        
        GET /supervisors/{id}/officers/
        """
        try:
            supervisor = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Supervisor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todas las asignaciones activas del supervisor
        active_assignments = SupervisorAssignment.objects.filter(
            supervisor=supervisor,
            end_date__isnull=True
        ).select_related('officer')
        
        officers = [assignment.officer for assignment in active_assignments]
        serializer = OfficerSerializer(officers, many=True)
        
        return Response({
            'success': True,
            'supervisor': {
                'id': supervisor.id,
                'name': supervisor.name,
                'email': supervisor.email,
                'badge_number': supervisor.badge_number,
                'rank': supervisor.rank,
            },
            'officers_count': len(officers),
            'officers': serializer.data
        }, status=status.HTTP_200_OK)
