from api.core.views import BaseViewSet
from .models import AlertType, Alert
from .serializers import AlertTypeSerializer, AlertSerializer


class AlertTypeViewSet(BaseViewSet):
    queryset = AlertType.objects.all()
    serializer_class = AlertTypeSerializer


class AlertViewSet(BaseViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer