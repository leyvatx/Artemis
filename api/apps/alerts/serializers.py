from rest_framework import serializers
from api.core.serializers import RelatedAttrField
from .models import AlertType, Alert


class AlertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertType
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    alert_type_name = RelatedAttrField('type.name')
    user_name = RelatedAttrField('user.name')
    acknowledged_by_name = RelatedAttrField('acknowledged_by.name')

    class Meta:
        model = Alert
        fields = ['id', 'user', 'type', 'alert_type_name', 'user_name', 'level', 'status', 'description', 'location', 'created_at', 'acknowledged_at', 'acknowledged_by', 'acknowledged_by_name', 'resolution_notes']