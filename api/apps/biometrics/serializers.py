from rest_framework import serializers
from .models import MetricType, BiometricRecord

class MetricTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricType
        fields = '__all__'

class BiometricRecordSerializer(serializers.ModelSerializer):
    metric_type_name = serializers.CharField(source='metric_type.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = BiometricRecord
        fields = ['id', 'user', 'metric_type', 'metric_type_name', 'user_name', 'value', 'recorded_at']