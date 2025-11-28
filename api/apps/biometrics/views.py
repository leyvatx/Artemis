import sys
import os
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status as http_status

from core.views import BaseViewSet
from .models import BPM, MLPrediction
from .serializers import BPMSerializer, MLPredictionSerializer
from apps.events import EventLogger
from apps.alerts.models import Alert, AlertType

# Importar el servicio ML
ML_PATH = os.path.join(settings.BASE_DIR, '..', 'ML')
if ML_PATH not in sys.path:
    sys.path.insert(0, ML_PATH)

try:
    from ml_service import ml_service
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️ WARNING: ML service not available: {e}")


class BPMViewSet(BaseViewSet):
    """ViewSet for simple BPM sensor readings with ML integration."""
    queryset = BPM.objects.all()
    serializer_class = BPMSerializer

    def create(self, request, *args, **kwargs):
        """
        Create BPM record and run ML analysis.
        
        Flow:
        1. Validate and save BPM
        2. Get recent BPM history for user
        3. Run ML analysis
        4. Save ML prediction
        5. Create alert if needed
        6. Log event
        7. Return response with ML results
        """
        # 1. Call superclass to validate and create the BPM instance
        response = super().create(request, *args, **kwargs)
        
        if response.status_code != http_status.HTTP_201_CREATED:
            return response
        
        # Get created BPM instance (BaseViewSet wraps data in 'data' key)
        bpm_data = response.data.get('data', {})
        bpm_id = bpm_data.get('id')
        bpm_instance = BPM.objects.get(pk=bpm_id)
        user = bpm_instance.user
        heart_rate = bpm_instance.value
        
        # Determine user for logging
        user_id = None
        try:
            if isinstance(request.data, dict):
                user_id = request.data.get('user_id')
        except Exception:
            user_id = None
        
        log_user = user_id if user_id is not None else request.user
        
        # 2. Get recent BPM history (last 10 readings)
        recent_bpms = BPM.objects.filter(
            user=user
        ).order_by('-created_at')[:10].values_list('value', flat=True)
        
        recent_hrs = list(recent_bpms) if recent_bpms else None
        
        # 3. Run ML analysis (if available)
        ml_result = None
        alert_created = None
        
        if ML_AVAILABLE:
            try:
                ml_result = ml_service.analyze_biometric_data(
                    heart_rate=heart_rate,
                    user_id=user.id,
                    recent_hrs=recent_hrs,
                    timestamp=bpm_instance.created_at.isoformat()
                )
                
                # 4. Save ML prediction
                prediction = ml_result['prediction']
                ml_prediction = MLPrediction.objects.create(
                    user=user,
                    bpm_record=bpm_instance,
                    stress_score=prediction['stress_score'],
                    stress_level=prediction['stress_level'],
                    severity=prediction['severity'],
                    requires_alert=prediction['requires_alert'],
                    alert_probability=prediction['alert_probability'],
                    is_anomaly=prediction['is_anomaly'],
                    hr_zone=prediction.get('hr_zone', ''),
                    ml_metadata=prediction.get('metadata', {})
                )
                
                # 5. Create alert if needed
                if ml_result['alert']:
                    alert_data = ml_result['alert']
                    
                    # Get or create AlertType
                    alert_type, _ = AlertType.objects.get_or_create(
                        name=alert_data['alert_type'],
                        defaults={
                            'default_level': alert_data['severity'],
                            'description': f"ML-generated alert: {alert_data['alert_type']}",
                            'is_active': True
                        }
                    )
                    
                    # Map ML severity to Django Alert level
                    severity_map = {
                        'CRITICAL': 'Critical',
                        'HIGH': 'High',
                        'MEDIUM': 'Medium',
                        'LOW': 'Low'
                    }
                    
                    # Create alert
                    alert_created = Alert.objects.create(
                        user=user,
                        type=alert_type,
                        level=severity_map.get(alert_data['severity'], 'Medium'),
                        status='Pending',
                        description=alert_data['message'],
                        location=''  # Could be populated from GPS data if available
                    )
                    
                    # Link alert to prediction
                    ml_prediction.alert = alert_created
                    ml_prediction.save()
                    
                    # Log alert event
                    EventLogger.log_event(
                        user=log_user,
                        title=f"ML Alert: {alert_data['alert_type']}",
                        category="Alert_Triggered",
                        description=f"ML detected {alert_data['severity']} alert: {alert_data['message'][:100]}",
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                
            except Exception as e:
                # Log error but don't fail the request
                print(f"⚠️ ML analysis error: {e}")
                EventLogger.log_event(
                    user=log_user,
                    title="ML Analysis Error",
                    category="System_Error",
                    description=f"Error during ML analysis: {str(e)}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
        
        # 6. Log BPM creation event
        EventLogger.log_event(
            user=log_user,
            title="BPM Record Created",
            category="Biometric_Capture_Success",
            description=f"BPM reading: {heart_rate} bpm" + (
                f" - ML: Stress {ml_result['prediction']['stress_score']:.1f}/100" 
                if ml_result else ""
            ),
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # 7. Enrich response with ML data
        response_data = response.data.copy()
        response_data['ml_analysis'] = {
            'available': ML_AVAILABLE,
            'prediction': {
                'stress_score': ml_result['prediction']['stress_score'],
                'stress_level': ml_result['prediction']['stress_level'],
                'severity': ml_result['prediction']['severity'],
                'requires_alert': ml_result['prediction']['requires_alert'],
                'is_anomaly': ml_result['prediction']['is_anomaly'],
            } if ml_result else None,
            'alert_created': alert_created.id if alert_created else None,
            'should_notify': ml_result.get('should_notify', False) if ml_result else False
        }
        
        return Response(response_data, status=http_status.HTTP_201_CREATED)

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