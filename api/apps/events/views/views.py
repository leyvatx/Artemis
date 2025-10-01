from rest_framework import viewsets
from ..models.models import Event
from ..serializers.serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
