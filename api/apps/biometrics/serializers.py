from rest_framework import serializers
from core.serializers import RelatedAttrField
from .models import MetricType, BiometricRecord


class MetricTypeSerializer(serializers.ModelSerializer):
    records_count = serializers.SerializerMethodField()

    class Meta:
        model = MetricType
        fields = ['id', 'name', 'description', 'unit', 'min_value', 'max_value', 'is_active', 'records_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_records_count(self, obj):
        return obj.records.count()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Metric name must be at least 2 characters long.")
        return value.strip()

    def validate(self, data):
        min_val = data.get('min_value')
        max_val = data.get('max_value')
        
        if min_val is not None and max_val is not None and min_val > max_val:
            raise serializers.ValidationError("Minimum value cannot be greater than maximum value.")
        
        return data


class BiometricRecordSerializer(serializers.ModelSerializer):
    metric_type_name = serializers.CharField(source='metric_type.name', read_only=True)
    metric_type_unit = serializers.CharField(source='metric_type.unit', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = BiometricRecord
        fields = [
            'id', 'user', 'metric_type', 'user_name', 'user_email',
            'metric_type_name', 'metric_type_unit', 'value', 'notes',
            'recorded_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'recorded_at']

    def validate_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Value cannot be negative.")
        return value

    def validate(self, data):
        metric_type = data.get('metric_type')
        value = data.get('value')
        
        if metric_type:
            if metric_type.min_value is not None and value < metric_type.min_value:
                raise serializers.ValidationError(
                    f"Value ({value}) is below minimum threshold ({metric_type.min_value})."
                )
            if metric_type.max_value is not None and value > metric_type.max_value:
                raise serializers.ValidationError(
                    f"Value ({value}) exceeds maximum threshold ({metric_type.max_value})."
                )
        
        return data


class BiometricRecordDetailSerializer(BiometricRecordSerializer):
    """Extended serializer with full related object details"""
    metric_type_details = MetricTypeSerializer(source='metric_type', read_only=True)

    class Meta(BiometricRecordSerializer.Meta):
        fields = BiometricRecordSerializer.Meta.fields + ['metric_type_details']
