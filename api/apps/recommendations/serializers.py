from rest_framework import serializers
from core.serializers import RelatedAttrField
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    alert_description = serializers.CharField(source='alert.description', read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            'recommendation_id', 'user', 'user_name', 'user_email',
            'alert', 'alert_description', 'message', 'category', 'priority',
            'is_active', 'acknowledged_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value.strip()

    def validate_category(self, value):
        valid_categories = dict(Recommendation.CATEGORY_CHOICES)
        if value not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Choose from: {list(valid_categories.keys())}")
        return value

    def validate_priority(self, value):
        valid_priorities = dict(Recommendation.PRIORITY_CHOICES)
        if value not in valid_priorities:
            raise serializers.ValidationError(f"Invalid priority. Choose from: {list(valid_priorities.keys())}")
        return value
