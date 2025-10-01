from rest_framework import viewsets
from .models import GeoLocation
from .serializers import GeoLocationSerializer

class GeoLocationViewSet(viewsets.ModelViewSet):
    queryset = GeoLocation.objects.all()
    serializer_class = GeoLocationSerializer
