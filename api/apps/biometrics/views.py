from api.core.views import BaseViewSet
from .models import MetricType, BiometricRecord
from .serializers import MetricTypeSerializer, BiometricRecordSerializer


class MetricTypeViewSet(BaseViewSet):
    queryset = MetricType.objects.all()
    serializer_class = MetricTypeSerializer


class BiometricRecordViewSet(BaseViewSet):
    queryset = BiometricRecord.objects.all()
    serializer_class = BiometricRecordSerializer