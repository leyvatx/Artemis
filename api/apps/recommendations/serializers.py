from rest_framework import serializers
from .models import Recommendation

class RecommendationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    alert_message = serializers.CharField(source='alert.message', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['recommendation_id', 'user', 'user_name', 'alert', 'alert_message', 'message', 'category', 'created_at']