from rest_framework import serializers
from .models import MetricType, Biometric

class MetricTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricType
        fields = '__all__'

class BiometricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biometric
        fields = '__all__'