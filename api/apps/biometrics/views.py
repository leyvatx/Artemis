from core.views import BaseViewSet
from .models import BPM
from .ml_models import MLPrediction, MLAlert
from .serializers import (
    BPMSerializer, 
    MLPredictionSerializer, 
    MLAlertSerializer,
    MLAlertDetailSerializer
)
from apps.events import EventLogger
from apps.users.models import SupervisorAssignment
from .ml_service import get_ml_service
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class BPMViewSet(BaseViewSet):
    """ViewSet for simple BPM sensor readings."""
    queryset = BPM.objects.all()
    serializer_class = BPMSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar por supervisor/officer role y officer_id
        - Supervisores: ven BPM de sus oficiales asignados
        - Oficiales: ven solo su propio BPM
        """
        user = self.request.user
        queryset = BPM.objects.all().order_by('-created_at')
        
        # Si es oficial, solo ve su propio BPM
        if user.role and user.role.name == 'officer':
            queryset = queryset.filter(user=user)
        # Si es supervisor, ve BPM de sus oficiales asignados
        elif user.role and user.role.name == 'supervisor':
            assigned_officers = SupervisorAssignment.objects.filter(
                supervisor=user,
                end_date__isnull=True
            ).values_list('officer_id', flat=True)
            queryset = queryset.filter(user_id__in=assigned_officers)
        else:
            queryset = BPM.objects.none()
        
        # También filtrar por officer_id si se proporciona en query params
        officer_id = self.request.query_params.get('officer', None)
        if officer_id:
            queryset = queryset.filter(user_id=officer_id)
        
        return queryset

    def create(self, request, *args, **kwargs):
        # Call superclass to validate and create the BPM instance. The serializer
        # expects `user_id` in the payload.
        response = super().create(request, *args, **kwargs)

        # Determine user for logging: prefer explicit user_id from payload,
        # otherwise fall back to authenticated request.user (EventLogger handles id/instance/anonymous).
        user_id = None
        try:
            # Try to read from request data first
            if isinstance(request.data, dict):
                user_id = request.data.get('user_id')
        except Exception:
            user_id = None

        log_user = user_id if user_id is not None else request.user

        EventLogger.log_event(
            user=log_user,
            title="BPM Record Created",
            category="Biometric_Capture_Success",
            description="BPM reading created",
            ip_address=request.META.get('REMOTE_ADDR')
        )

        # ========== INTEGRACIÓN ML (NO BLOQUEA EL FLUJO) ==========
        # El BPM ya fue guardado exitosamente, ahora analizamos con ML
        # Si falla, el BPM ya está guardado y el ESP32 no se ve afectado
        try:
            # Obtener la instancia de BPM creada
            # response.data tiene estructura: {'success': True, 'data': {'id': X, ...}, 'message': '...'}
            response_data = response.data.get('data', {})
            bpm_id = response_data.get('id') if isinstance(response_data, dict) else None
            
            if bpm_id:
                bpm_instance = BPM.objects.get(id=bpm_id)
                
                # Ejecutar análisis ML en segundo plano
                ml_service = get_ml_service()
                ml_result = ml_service.analyze_bpm(bpm_instance)
                
                # Loguear resultado del análisis ML
                if ml_result['success']:
                    # Mostrar si se guardó predicción o no
                    if ml_result.get('prediction_saved'):
                        logger.info(
                            f"ML Analysis: BPM {bpm_id} -> "
                            f"Stress={ml_result['stress_score']:.1f}, "
                            f"Pattern={ml_result.get('pattern_type', 'N/A')}, "
                            f"Prediction SAVED, Alert={ml_result['alert_created']}"
                        )
                    else:
                        logger.debug(
                            f"ML Analysis: BPM {bpm_id} -> "
                            f"Stress={ml_result['stress_score']:.1f}, "
                            f"Normal - No prediction saved"
                        )
                    
                    # Si se creó una alerta crítica, registrar evento
                    if ml_result['alert_created'] and ml_result['severity'] in ['CRITICAL', 'HIGH']:
                        EventLogger.log_event(
                            user=log_user,
                            title=f"ML Alert Created - {ml_result['severity']}",
                            category="ML_Alert_Triggered",
                            description=f"Alerta ML automática: Severidad {ml_result['severity']}",
                            ip_address=request.META.get('REMOTE_ADDR')
                        )
                else:
                    logger.error(f"ML Analysis failed for BPM {bpm_id}: {ml_result.get('error')}")
            else:
                logger.warning(f"No se pudo obtener bpm_id de response.data: {response.data}")
                    
        except Exception as e:
            # Si el análisis ML falla, solo loguear el error
            # El BPM YA FUE GUARDADO, así que el ESP32 no se ve afectado
            logger.error(f"Error en análisis ML (no afecta flujo): {e}", exc_info=True)
        # ========== FIN INTEGRACIÓN ML ==========

        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)

        EventLogger.log_event(
            user=request.user,
            title="BPM Record Deleted",
            category="Biometric_Data_Deleted",
            description="BPM reading deleted",
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return response


class MLPredictionViewSet(BaseViewSet):
    """ViewSet para consultar predicciones ML"""
    queryset = MLPrediction.objects.all()
    serializer_class = MLPredictionSerializer
    
    def get_queryset(self):
        """Filtrar por officer_id si se proporciona en query params"""
        queryset = MLPrediction.objects.all().order_by('-created_at')
        officer_id = self.request.query_params.get('officer', None)
        if officer_id:
            queryset = queryset.filter(user_id=officer_id)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Obtener predicciones de un usuario específico"""
        predictions = self.queryset.filter(user_id=user_id).order_by('-created_at')[:50]
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/latest')
    def latest_by_user(self, request, user_id=None):
        """Obtener la última predicción de un usuario"""
        prediction = self.queryset.filter(user_id=user_id).order_by('-created_at').first()
        if not prediction:
            return Response(
                {'error': 'No predictions found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(prediction)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/risk-summary')
    def risk_summary(self, request, user_id=None):
        """Obtener resumen de riesgo de un usuario"""
        hours = int(request.query_params.get('hours', 24))
        ml_service = get_ml_service()
        summary = ml_service.get_user_risk_summary(user_id, hours)
        return Response(summary)
    
    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge(self, request, pk=None):
        """Marcar predicción como reconocida"""
        prediction = self.get_object()
        
        from django.utils import timezone
        prediction.status = 'Acknowledged'
        prediction.save()
        
        EventLogger.log_event(
            user=request.user if hasattr(request, 'user') else None,
            title=f"ML Prediction Acknowledged",
            category="ML_Prediction_Acknowledged",
            description=f"Predicción ML {prediction.id} reconocida",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        serializer = self.get_serializer(prediction)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """Marcar predicción como resuelta con justificación"""
        prediction = self.get_object()
        
        from django.utils import timezone
        
        resolution_notes = request.data.get('resolution_notes', '')
        if not resolution_notes:
            return Response(
                {'error': 'Se requiere una justificación para resolver la predicción'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prediction.status = 'Resolved'
        prediction.resolved_at = timezone.now()
        prediction.resolution_notes = resolution_notes
        
        # Intentar obtener el usuario autenticado
        if hasattr(request, 'user') and request.user.is_authenticated:
            prediction.resolved_by = request.user
        
        prediction.save()
        
        EventLogger.log_event(
            user=request.user if hasattr(request, 'user') else None,
            title=f"ML Prediction Resolved",
            category="ML_Prediction_Resolved",
            description=f"Predicción ML {prediction.id} resuelta: {resolution_notes[:100]}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        serializer = self.get_serializer(prediction)
        return Response(serializer.data)


class MLAlertViewSet(BaseViewSet):
    """ViewSet para alertas ML"""
    queryset = MLAlert.objects.all()
    serializer_class = MLAlertSerializer
    
    def get_queryset(self):
        """Filtrar por officer_id si se proporciona en query params"""
        queryset = MLAlert.objects.all().order_by('-created_at')
        officer_id = self.request.query_params.get('officer', None)
        if officer_id:
            queryset = queryset.filter(user_id=officer_id)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MLAlertDetailSerializer
        return MLAlertSerializer
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """Obtener todas las alertas pendientes"""
        alerts = self.queryset.filter(status='Pending').order_by('-created_at')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='critical')
    def critical(self, request):
        """Obtener alertas críticas pendientes"""
        alerts = self.queryset.filter(
            status='Pending',
            severity='CRITICAL'
        ).order_by('-created_at')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Obtener alertas de un usuario específico"""
        alerts = self.queryset.filter(user_id=user_id).order_by('-created_at')[:50]
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge(self, request, pk=None):
        """Marcar alerta como reconocida"""
        alert = self.get_object()
        
        from django.utils import timezone
        alert.status = 'Acknowledged'
        alert.acknowledged_at = timezone.now()
        
        # Intentar obtener el usuario autenticado
        if hasattr(request, 'user') and request.user.is_authenticated:
            alert.acknowledged_by = request.user
        
        alert.save()
        
        EventLogger.log_event(
            user=request.user,
            title=f"ML Alert Acknowledged",
            category="ML_Alert_Acknowledged",
            description=f"Alerta ML {alert.id} reconocida",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """Marcar alerta como resuelta"""
        alert = self.get_object()
        
        from django.utils import timezone
        alert.status = 'Resolved'
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('resolution_notes', '')
        alert.save()
        
        EventLogger.log_event(
            user=request.user,
            title=f"ML Alert Resolved",
            category="ML_Alert_Resolved",
            description=f"Alerta ML {alert.id} resuelta",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
