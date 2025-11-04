from rest_framework import serializers
from core.serializers import RelatedAttrField
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Event
        fields = [
            'event_id', 'user', 'user_name', 'user_email', 'title',
            'description', 'category', 'ip_address', 'user_agent',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def validate_category(self, value):
        valid_categories = dict(Event.EVENT_CATEGORIES)
        if value not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Choose from: {list(valid_categories.keys())}")
        return value
