from core.views import BaseViewSet
from .models import BPM
from .serializers import BPMSerializer
from apps.events import EventLogger
from rest_framework import status
from rest_framework.response import Response


class BPMViewSet(BaseViewSet):
    """ViewSet for simple BPM sensor readings."""
    queryset = BPM.objects.all()
    serializer_class = BPMSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, dict):
            try:
                raw = request.body.decode('utf-8').strip()
                value = float(raw)
                user_id_hdr = request.META.get('HTTP_X_USER_ID') or request.GET.get('user_id')
                data = {'value': value}
                if user_id_hdr:
                    try:
                        data['user_id'] = int(user_id_hdr)
                    except Exception:
                        pass
            except Exception:
                data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(
            {'success': True, 'data': serializer.data, 'message': 'Created successfully'},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
        user_id = None
        try:
            if isinstance(data, dict):
                user_id = data.get('user_id')
        except Exception:
            user_id = None

        log_user = user_id if user_id is not None else request.user

        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')

        EventLogger.log_event(
            user=log_user,
            title="BPM Record Created",
            category="Biometric_Capture_Success",
            description="BPM reading created",
            ip_address=ip,
            user_agent=user_agent,
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