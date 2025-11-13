from rest_framework import serializers
from .models import AlertType, Alert, ALERT_LEVEL_CHOICES, ALERT_STATUS_CHOICES


class AlertTypeSerializer(serializers.ModelSerializer):
    alerts_count = serializers.SerializerMethodField()

    class Meta:
        model = AlertType
        fields = ['id', 'name', 'description', 'default_level', 'is_active', 'alerts_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_alerts_count(self, obj):
        return obj.alerts.count()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Alert type name must be at least 2 characters long.")
        return value.strip()


class AlertSerializer(serializers.ModelSerializer):
    alert_type_name = serializers.CharField(source='type.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.name', read_only=True, allow_null=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'user', 'type', 'user_name', 'user_email', 'alert_type_name',
            'level', 'status', 'description', 'location', 'created_at',
            'acknowledged_at', 'acknowledged_by', 'acknowledged_by_name',
            'resolution_notes', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_level(self, value):
        valid_levels = dict(ALERT_LEVEL_CHOICES)
        if value not in valid_levels:
            raise serializers.ValidationError(f"Invalid level. Choose from: {list(valid_levels.keys())}")
        return value

    def validate_status(self, value):
        valid_statuses = dict(ALERT_STATUS_CHOICES)
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {list(valid_statuses.keys())}")
        return value

    def validate(self, data):
        if data.get('status') == 'Acknowledged' and not data.get('acknowledged_by'):
            raise serializers.ValidationError({"acknowledged_by": "Acknowledging user is required when status is Acknowledged."})
        
        return data


class AlertDetailSerializer(AlertSerializer):
    """Extended serializer with full related object details"""
    type_details = AlertTypeSerializer(source='type', read_only=True)

    class Meta(AlertSerializer.Meta):
        fields = AlertSerializer.Meta.fields + ['type_details']
