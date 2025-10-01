import pytest
from django.test import TestCase
from ..models.models import Report
from ..serializers.serializers import ReportSerializer
from ..services.services import ReportService
from apps.users.models import User


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_create_report(self):
        report = Report.objects.create(
            user=self.user,
            report_type='Activity Report',
            content='Report content'
        )
        self.assertEqual(report.report_type, 'Activity Report')
        self.assertEqual(str(report), 'Activity Report by Test User')


class ReportSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_serialize_report(self):
        report = Report.objects.create(user=self.user, report_type='Test')
        serializer = ReportSerializer(report)
        self.assertEqual(serializer.data['report_type'], 'Test')


class ReportServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_generate_report(self):
        report = ReportService.generate_report(self.user, 'Daily Report', 'Content')
        self.assertEqual(report.report_type, 'Daily Report')

    def test_get_user_reports(self):
        ReportService.generate_report(self.user, 'Daily Report')
        reports = ReportService.get_user_reports(self.user)
        self.assertEqual(len(reports), 1)