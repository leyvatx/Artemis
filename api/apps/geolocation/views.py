from api.core.views import BaseViewSet
from .models import GeoLocation
from .serializers import GeoLocationSerializer


class GeoLocationViewSet(BaseViewSet):
    queryset = GeoLocation.objects.all()
    serializer_class = GeoLocationSerializer