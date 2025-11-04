from core.views import BaseViewSet
from .models import Event
from .serializers import EventSerializer


class EventViewSet(BaseViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer