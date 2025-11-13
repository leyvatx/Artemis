from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    # Use SerializerMethodField so we handle events without a linked user
    user_name = serializers.SerializerMethodField(read_only=True)
    user_email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'event_id', 'user', 'user_name', 'user_email', 'title',
            'description', 'category', 'ip_address', 'user_agent',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_user_name(self, obj):
        return obj.user.name if getattr(obj, 'user', None) else None

    def get_user_email(self, obj):
        return obj.user.email if getattr(obj, 'user', None) else None

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def validate_category(self, value):
        valid_categories = dict(Event.EVENT_CATEGORIES)
        if value not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Choose from: {list(valid_categories.keys())}")
        return value
