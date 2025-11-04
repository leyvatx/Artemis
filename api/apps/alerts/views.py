from core.views import BaseViewSet
from .models import AlertType, Alert
from .serializers import AlertTypeSerializer, AlertSerializer
from apps.events import EventLogger  # ← NUEVO: Para registrar eventos


class AlertTypeViewSet(BaseViewSet):
    queryset = AlertType.objects.all()
    serializer_class = AlertTypeSerializer


class AlertViewSet(BaseViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear una alerta y registrar evento"""
        response = super().create(request, *args, **kwargs)
        
        # ← NUEVO: Registrar evento de alerta disparada
        alert_data = response.data
        EventLogger.log_event(
            user=request.user,
            title=f"Alert Triggered: {alert_data.get('name', 'Unknown')}",
            category="Alert_Triggered",
            description=f"Nueva alerta: {alert_data.get('description', '')}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar una alerta y registrar evento"""
        response = super().destroy(request, *args, **kwargs)
        
        # ← NUEVO: Registrar evento de alerta resuelta
        EventLogger.log_event(
            user=request.user,
            title="Alert Resolved",
            category="Alert_Resolved",
            description="Alerta eliminada/resuelta",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return response