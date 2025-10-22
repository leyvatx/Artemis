from rest_framework import serializers
from api.core.serializers import RelatedAttrField
from .models import GeoLocation


class GeoLocationSerializer(serializers.ModelSerializer):
    user_name = RelatedAttrField('user.name')

    class Meta:
        model = GeoLocation
        fields = ['geolocation_id', 'user', 'user_name', 'location', 'created_at']