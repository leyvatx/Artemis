from rest_framework import serializers
from api.core.serializers import RelatedAttrField
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    user_name = RelatedAttrField('user.name')

    class Meta:
        model = Event
        fields = ['event_id', 'user', 'user_name', 'title', 'description', 'category', 'created_at']