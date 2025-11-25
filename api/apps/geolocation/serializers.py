from rest_framework import serializers
from .models import GeoLocation
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.serializers import UserSummarySerializer


class GeoLocationSerializer(serializers.ModelSerializer):
    user_summary = UserSummarySerializer(source='user', read_only=True)

    class Meta:
        model = GeoLocation
        fields = [
            'geolocation_id', 'user', 'user_summary',
            'latitude', 'longitude', 'accuracy', 'location_name',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate_accuracy(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Accuracy cannot be negative.")
        return value
