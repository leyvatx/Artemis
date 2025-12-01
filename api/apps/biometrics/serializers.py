from rest_framework import serializers
from apps.users.models import User as UserModel
from .models import BPM
from .ml_models import MLPrediction, MLAlert


class BPMSerializer(serializers.ModelSerializer):
    # Expose only user_id (writeable/readable) instead of nested user object
    user_id = serializers.IntegerField(write_only=False, required=True)

    class Meta:
        model = BPM
        fields = ['id', 'user_id', 'value']

    def validate_value(self, value):
        if value is None:
            raise serializers.ValidationError("Value is required.")
        try:
            val = float(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Value must be numeric.")
        return val

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        if user_id is None:
            raise serializers.ValidationError({'user_id': 'user_id is required.'})
        try:
            user = UserModel.objects.get(pk=int(user_id))
        except UserModel.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'User with given id does not exist.'})

        bpm = BPM.objects.create(user=user, **validated_data)
        return bpm

    def to_representation(self, instance):
        # Represent as {id, user_id, value}
        ret = super().to_representation(instance)
        ret['user_id'] = instance.user_id if instance.user_id is not None else None
        return ret


class MLPredictionSerializer(serializers.ModelSerializer):
    """Serializer para predicciones ML"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    bpm_value = serializers.FloatField(source='bpm.value', read_only=True)
    resolved_by_name = serializers.CharField(
        source='resolved_by.name', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = MLPrediction
        fields = [
            'id', 'bpm', 'user', 'user_name', 'bpm_value',
            'stress_score', 'stress_level', 'requires_alert',
            'alert_probability', 'severity', 'is_anomaly',
            'anomaly_score', 'hr_zone', 'hr_variability',
            'metadata', 'status', 'resolved_at', 'resolved_by',
            'resolved_by_name', 'resolution_notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class MLAlertSerializer(serializers.ModelSerializer):
    """Serializer para alertas ML"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    acknowledged_by_name = serializers.CharField(
        source='acknowledged_by.name', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = MLAlert
        fields = [
            'id', 'user', 'user_name', 'user_email', 'prediction',
            'alert_type', 'severity', 'message', 'action_required',
            'heart_rate', 'stress_score', 'stress_level',
            'requires_immediate_action', 'is_anomaly', 'status',
            'acknowledged_at', 'acknowledged_by', 'acknowledged_by_name',
            'resolved_at', 'resolution_notes', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class MLAlertDetailSerializer(MLAlertSerializer):
    """Serializer detallado con predicción completa"""
    prediction_details = MLPredictionSerializer(source='prediction', read_only=True)
    
    class Meta(MLAlertSerializer.Meta):
        fields = MLAlertSerializer.Meta.fields + ['prediction_details']
