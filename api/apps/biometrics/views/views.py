from rest_framework import viewsets
from ..models.models import MetricType, Biometric
from ..serializers.serializers import MetricTypeSerializer, BiometricSerializer

class MetricTypeViewSet(viewsets.ModelViewSet):
    queryset = MetricType.objects.all()
    serializer_class = MetricTypeSerializer

class BiometricViewSet(viewsets.ModelViewSet):
    queryset = Biometric.objects.all()
    serializer_class = BiometricSerializer
