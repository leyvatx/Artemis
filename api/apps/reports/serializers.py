from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    officer_summary = serializers.SerializerMethodField()
    supervisor_summary = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'report_id',
            'report_type', 'title', 'content', 'summary', 'status',
            'created_at', 'updated_at', 'generated_at', 'sent_at',
            'officer_summary', 'supervisor_summary'
        ]
        read_only_fields = ['created_at', 'updated_at', 'generated_at', 'sent_at']

    def get_officer_summary(self, obj):
        officer = obj.officer
        return {
            "id": officer.id,
            "name": officer.name,
            "badge_number": officer.badge_number,
            "rank": officer.rank,
            "status": officer.status,
            "picture": officer.picture.url if officer.picture else None,
        }

    def get_supervisor_summary(self, obj):
        supervisor = obj.supervisor
        return {
            "id": supervisor.id,
            "name": supervisor.name,
            "email": supervisor.email,
            "status": supervisor.status,
            "role": supervisor.role.name if supervisor.role else None,
        }