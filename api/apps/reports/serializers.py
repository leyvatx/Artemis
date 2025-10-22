from rest_framework import serializers
from api.core.serializers import RelatedAttrField
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    user_name = RelatedAttrField('user.name')

    class Meta:
        model = Report
        fields = ['report_id', 'user', 'user_name', 'report_type', 'content', 'created_at']