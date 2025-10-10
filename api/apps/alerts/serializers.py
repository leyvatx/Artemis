from rest_framework import serializers
from .models import AlertType, Alert

class AlertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertType
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    alert_type_name = serializers.CharField(source='type.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'user', 'type', 'alert_type_name', 'user_name', 'level', 'status', 'description', 'location', 'created_at', 'acknowledged_at', 'acknowledged_by', 'acknowledged_by_name', 'resolution_notes']