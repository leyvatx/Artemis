from rest_framework import serializers
from api.core.serializers import RelatedAttrField
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    user_name = RelatedAttrField('user.name')
    alert_message = RelatedAttrField('alert.message')

    class Meta:
        model = Recommendation
        fields = ['recommendation_id', 'user', 'user_name', 'alert', 'alert_message', 'message', 'category', 'created_at']