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
from apps.alerts.models import Alert, AlertType
from apps.biometrics.models import BPM
from apps.geolocation.models import GeoLocation
from apps.events.models import Event
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


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
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Obtener estadísticas generales del sistema.
        GET /users/statistics/
        """
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # Conteos generales
        total_users = User.objects.count()
        supervisors = User.objects.filter(supervisor_assignments__isnull=False).distinct().count()
        officers = User.objects.filter(officer_assignments__isnull=False).distinct().count()
        active_users = User.objects.filter(status='Active').count()
        inactive_users = User.objects.filter(status='Inactive').count()
        
        # Asignaciones
        total_assignments = SupervisorAssignment.objects.count()
        active_assignments = SupervisorAssignment.objects.filter(end_date__isnull=True).count()
        completed_assignments = SupervisorAssignment.objects.filter(end_date__isnull=False).count()
        
        # Alertas
        total_alerts = Alert.objects.count()
        pending_alerts = Alert.objects.filter(status='Pending').count()
        critical_alerts = Alert.objects.filter(level='Critical').count()
        alerts_last_7_days = Alert.objects.filter(created_at__gte=last_7_days).count()
        alerts_by_level = Alert.objects.values('level').annotate(count=Count('id'))
        
        # Biometría
        total_biometric_records = BPM.objects.count()
        biometric_last_7_days = BPM.objects.filter(created_at__gte=last_7_days).count()
        
        # Geolocalización
        total_locations = GeoLocation.objects.count()
        locations_last_7_days = GeoLocation.objects.filter(created_at__gte=last_7_days).count()
        
        # Eventos
        total_events = Event.objects.count()
        events_last_7_days = Event.objects.filter(created_at__gte=last_7_days).count()
        
        return Response({
            'success': True,
            'timestamp': now.isoformat(),
            'users': {
                'total': total_users,
                'supervisors': supervisors,
                'officers': officers,
                'active': active_users,
                'inactive': inactive_users,
            },
            'assignments': {
                'total': total_assignments,
                'active': active_assignments,
                'completed': completed_assignments,
            },
            'alerts': {
                'total': total_alerts,
                'pending': pending_alerts,
                'critical': critical_alerts,
                'last_7_days': alerts_last_7_days,
                'by_level': list(alerts_by_level),
            },
            'biometrics': {
                'total_records': total_biometric_records,
                'last_7_days': biometric_last_7_days,
            },
            'locations': {
                'total_records': total_locations,
                'last_7_days': locations_last_7_days,
            },
            'events': {
                'total': total_events,
                'last_7_days': events_last_7_days,
            }
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
    
    @action(detail=True, methods=['get'], url_path='statistics')
    def statistics(self, request, pk=None):
        """
        Obtener estadísticas de un supervisor específico.
        
        GET /supervisors/{id}/statistics/
        """
        try:
            supervisor = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Supervisor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # Oficiales bajo supervisión
        active_officers = SupervisorAssignment.objects.filter(
            supervisor=supervisor,
            end_date__isnull=True
        ).select_related('officer')
        officer_ids = [a.officer.id for a in active_officers]
        officers_count = len(officer_ids)
        
        # Alertas de sus oficiales
        total_alerts = Alert.objects.filter(user_id__in=officer_ids).count()
        pending_alerts = Alert.objects.filter(user_id__in=officer_ids, status='Pending').count()
        critical_alerts = Alert.objects.filter(user_id__in=officer_ids, level='Critical').count()
        alerts_last_7_days = Alert.objects.filter(user_id__in=officer_ids, created_at__gte=last_7_days).count()
        
        # Biometría de sus oficiales
        biometric_records = BPM.objects.filter(user_id__in=officer_ids).count()
        biometric_last_7_days = BPM.objects.filter(user_id__in=officer_ids, created_at__gte=last_7_days).count()
        
        # Ubicaciones de sus oficiales
        location_records = GeoLocation.objects.filter(user_id__in=officer_ids).count()
        location_last_7_days = GeoLocation.objects.filter(user_id__in=officer_ids, created_at__gte=last_7_days).count()
        
        # Eventos de sus oficiales
        events = Event.objects.filter(user_id__in=officer_ids).count()
        events_last_7_days = Event.objects.filter(user_id__in=officer_ids, created_at__gte=last_7_days).count()
        
        # Estados de los oficiales
        active_officers_count = User.objects.filter(id__in=officer_ids, status='Active').count()
        inactive_officers_count = User.objects.filter(id__in=officer_ids, status='Inactive').count()
        
        return Response({
            'success': True,
            'supervisor': {
                'id': supervisor.id,
                'name': supervisor.name,
                'email': supervisor.email,
                'badge_number': supervisor.badge_number,
                'rank': supervisor.rank,
            },
            'timestamp': now.isoformat(),
            'officers': {
                'total': officers_count,
                'active': active_officers_count,
                'inactive': inactive_officers_count,
            },
            'alerts': {
                'total': total_alerts,
                'pending': pending_alerts,
                'critical': critical_alerts,
                'last_7_days': alerts_last_7_days,
            },
            'biometrics': {
                'total_records': biometric_records,
                'last_7_days': biometric_last_7_days,
            },
            'locations': {
                'total_records': location_records,
                'last_7_days': location_last_7_days,
            },
            'events': {
                'total': events,
                'last_7_days': events_last_7_days,
            }
        }, status=status.HTTP_200_OK)
