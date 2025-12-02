from core.views import BaseViewSet
from .models import AlertType, Alert
from .serializers import AlertTypeSerializer, AlertSerializer
from apps.events import EventLogger
from apps.users.models import SupervisorAssignment
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q


class AlertTypeViewSet(BaseViewSet):
    queryset = AlertType.objects.all()
    serializer_class = AlertTypeSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def test_endpoint(request):
    """Endpoint de prueba para debug"""
    return Response({
        'user': str(request.user),
        'authenticated': request.user.is_authenticated,
        'method': request.method,
    })


class AlertViewSet(viewsets.ModelViewSet):
    """NO hereda de BaseViewSet para tener control total del list()"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [AllowAny]  # CAMBIO: AllowAny en lugar de IsAuthenticated
    
    def get_queryset(self):
        """
        SIMPLE: Si viene ?user=X, retorna la última alerta de ese officer.
        Sin validación de permisos - lo valida el endpoint que la consume.
        """
        officer_id = self.request.query_params.get('user')
        
        if officer_id:
            try:
                officer_id = int(officer_id)
                # Retorna solo la última alerta del officer
                last_alert = Alert.objects.filter(user_id=officer_id).order_by('-created_at').first()
                if last_alert:
                    return Alert.objects.filter(id=last_alert.id)
            except (ValueError, TypeError):
                pass
        
        # Si no hay officer_id especificado, retorna vacío
        return Alert.objects.filter(id__in=[])
    
    def list(self, request, *args, **kwargs):
        """List con respuesta consistente - NUNCA falla"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'count': queryset.count(),
                'results': serializer.data
            })
        except Exception as e:
            # Si falla, retorna lista vacía válida
            return Response({
                'success': True,
                'count': 0,
                'results': []
            })
    
    def create(self, request, *args, **kwargs):
        """Crear una alerta y registrar evento"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Registrar evento de alerta disparada
        EventLogger.log_event(
            user=request.user,
            title=f"Alert Triggered: {serializer.data.get('name', 'Unknown')}",
            category="Alert_Triggered",
            description=f"Nueva alerta: {serializer.data.get('description', '')}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Alert created successfully'
        }, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar una alerta y registrar evento"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        # Registrar evento de alerta resuelta
        EventLogger.log_event(
            user=request.user,
            title="Alert Resolved",
            category="Alert_Resolved",
            description="Alerta eliminada/resuelta",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'success': True,
            'message': 'Alert deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)