from rest_framework import serializers
from core.serializers import RelatedAttrField
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Report
        fields = [
            'report_id', 'user', 'user_name', 'user_email',
            'report_type', 'title', 'content', 'summary', 'status',
            'created_at', 'updated_at', 'generated_at', 'sent_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'generated_at', 'sent_at']

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def validate_report_type(self, value):
        valid_types = dict(Report.REPORT_TYPE_CHOICES)
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid report type. Choose from: {list(valid_types.keys())}")
        return value

    def validate_status(self, value):
        valid_statuses = dict(Report.STATUS_CHOICES)
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {list(valid_statuses.keys())}")
        return value
