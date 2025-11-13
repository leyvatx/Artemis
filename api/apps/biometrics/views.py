from core.views import BaseViewSet
from .models import BPM
from .serializers import BPMSerializer
from apps.events import EventLogger


class BPMViewSet(BaseViewSet):
    """ViewSet for simple BPM sensor readings."""
    queryset = BPM.objects.all()
    serializer_class = BPMSerializer

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