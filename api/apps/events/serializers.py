from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Event
        fields = ['event_id', 'user', 'user_name', 'title', 'description', 'category', 'created_at']