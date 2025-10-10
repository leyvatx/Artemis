from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Report
        fields = ['report_id', 'user', 'user_name', 'report_type', 'content', 'created_at']