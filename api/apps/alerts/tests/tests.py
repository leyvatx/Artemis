import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models.models import AlertType, Alert
from ..serializers.serializers import AlertTypeSerializer, AlertSerializer
from ..services.services import AlertService, AlertTypeService
from apps.users.models import User


class AlertTypeModelTest(TestCase):
    def test_create_alert_type(self):
        at = AlertType.objects.create(type_name='Security Alert', default_level='High')
        self.assertEqual(at.type_name, 'Security Alert')
        self.assertEqual(str(at), 'Security Alert')


class AlertModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )
        self.alert_type = AlertType.objects.create(type_name='Test Alert', default_level='Low')

    def test_create_alert(self):
        alert = Alert.objects.create(
            user=self.user,
            alert_type=self.alert_type,
            description='Test alert'
        )
        self.assertEqual(alert.description, 'Test alert')
        self.assertEqual(str(alert), 'Alert for Test User - Test Alert')


class AlertTypeSerializerTest(TestCase):
    def test_serialize_alert_type(self):
        at = AlertType.objects.create(type_name='Test', default_level='Low')
        serializer = AlertTypeSerializer(at)
        self.assertEqual(serializer.data['type_name'], 'Test')


class AlertServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )
        AlertType.objects.create(type_name='Test Alert', default_level='Low')

    def test_create_alert(self):
        alert = AlertService.create_alert(self.user, 'Test Alert', 'Description')
        self.assertEqual(alert.description, 'Description')

    def test_create_invalid_alert_type(self):
        with self.assertRaises(ValidationError):
            AlertService.create_alert(self.user, 'Invalid Type', 'Description')


class AlertTypeServiceTest(TestCase):
    def test_create_alert_type(self):
        at = AlertTypeService.create_alert_type('New Alert Type', 'Medium')
        self.assertEqual(at.type_name, 'New Alert Type')

    def test_create_invalid_level(self):
        with self.assertRaises(ValidationError):
            AlertTypeService.create_alert_type('New Alert Type', 'Invalid')