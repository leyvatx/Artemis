from core.views import BaseViewSet
from .models import MetricType, BiometricRecord
from .serializers import MetricTypeSerializer, BiometricRecordSerializer
from apps.events import EventLogger  # ← NUEVO: Para registrar eventos


class MetricTypeViewSet(BaseViewSet):
    queryset = MetricType.objects.all()
    serializer_class = MetricTypeSerializer


class BiometricRecordViewSet(BaseViewSet):
    queryset = BiometricRecord.objects.all()
    serializer_class = BiometricRecordSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear un registro biométrico y registrar evento"""
        response = super().create(request, *args, **kwargs)
        
        # ← NUEVO: Registrar evento de éxito
        EventLogger.log_event(
            user=request.user,
            title="Biometric Record Created",
            category="Biometric_Capture_Success",
            description=f"Nuevo registro biométrico creado",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar un registro biométrico y registrar evento"""
        response = super().destroy(request, *args, **kwargs)
        
        # ← NUEVO: Registrar evento de eliminación
        EventLogger.log_event(
            user=request.user,
            title="Biometric Data Deleted",
            category="Biometric_Data_Deleted",
            description="Registro biométrico eliminado",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return response