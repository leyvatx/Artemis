from rest_framework import viewsets
from .models import MetricType, BiometricRecord
from .serializers import MetricTypeSerializer, BiometricRecordSerializer

class MetricTypeViewSet(viewsets.ModelViewSet):
    queryset = MetricType.objects.all()
    serializer_class = MetricTypeSerializer

class BiometricRecordViewSet(viewsets.ModelViewSet):
    queryset = BiometricRecord.objects.all()
    serializer_class = BiometricRecordSerializer