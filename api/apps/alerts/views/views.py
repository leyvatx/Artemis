from rest_framework import viewsets
from ..models.models import AlertType, Alert
from ..serializers.serializers import AlertTypeSerializer, AlertSerializer

class AlertTypeViewSet(viewsets.ModelViewSet):
    queryset = AlertType.objects.all()
    serializer_class = AlertTypeSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
