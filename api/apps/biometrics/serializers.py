from rest_framework import serializers
from apps.users.models import User as UserModel
from .models import BPM, MLPrediction


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
    """Serializer for ML prediction results."""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    bpm_value = serializers.FloatField(source='bpm_record.value', read_only=True)
    alert_id = serializers.IntegerField(source='alert.id', read_only=True, allow_null=True)
    
    class Meta:
        model = MLPrediction
        fields = [
            'id',
            'user_id',
            'bpm_value',
            'bpm_record',
            'stress_score',
            'stress_level',
            'severity',
            'requires_alert',
            'alert_probability',
            'is_anomaly',
            'hr_zone',
            'alert_id',
            'ml_metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
