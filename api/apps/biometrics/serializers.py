from rest_framework import serializers
from api.core.serializers import RelatedAttrField
from .models import MetricType, BiometricRecord


class MetricTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricType
        fields = '__all__'


class BiometricRecordSerializer(serializers.ModelSerializer):
    metric_type_name = RelatedAttrField('metric_type.name')
    user_name = RelatedAttrField('user.name')

    class Meta:
        model = BiometricRecord
        fields = ['id', 'user', 'metric_type', 'metric_type_name', 'user_name', 'value', 'recorded_at']