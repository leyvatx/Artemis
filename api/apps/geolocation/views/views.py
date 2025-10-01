from rest_framework import viewsets
from ..models.models import GeoLocation
from ..serializers.serializers import GeoLocationSerializer

class GeoLocationViewSet(viewsets.ModelViewSet):
    queryset = GeoLocation.objects.all()
    serializer_class = GeoLocationSerializer
