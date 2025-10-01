import pytest
from django.test import TestCase
from ..models.models import MetricType, Biometric
from ..serializers.serializers import MetricTypeSerializer, BiometricSerializer
from ..services.services import BiometricService, MetricTypeService
from apps.users.models import User


class MetricTypeModelTest(TestCase):
    def test_create_metric_type(self):
        mt = MetricType.objects.create(type_name='Heart Rate', unit='bpm')
        self.assertEqual(mt.type_name, 'Heart Rate')
        self.assertEqual(str(mt), 'Heart Rate')


class BiometricModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )
        self.metric_type = MetricType.objects.create(type_name='Heart Rate', unit='bpm')

    def test_create_biometric(self):
        bio = Biometric.objects.create(
            user=self.user,
            metric_type=self.metric_type,
            metric_value=75.5
        )
        self.assertEqual(bio.metric_value, 75.5)
        self.assertEqual(str(bio), 'Test User - Heart Rate: 75.5')


class MetricTypeSerializerTest(TestCase):
    def test_serialize_metric_type(self):
        mt = MetricType.objects.create(type_name='Temperature', unit='C')
        serializer = MetricTypeSerializer(mt)
        self.assertEqual(serializer.data['type_name'], 'Temperature')


class BiometricServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )
        MetricType.objects.create(type_name='Heart Rate', unit='bpm')

    def test_record_biometric_data(self):
        bio = BiometricService.record_biometric_data(self.user, 'Heart Rate', 80.0)
        self.assertEqual(bio.metric_value, 80.0)

    def test_record_invalid_metric_type(self):
        with self.assertRaises(ValidationError):
            BiometricService.record_biometric_data(self.user, 'Invalid Type', 80.0)


class MetricTypeServiceTest(TestCase):
    def test_create_metric_type(self):
        mt = MetricTypeService.create_metric_type('Blood Pressure', 'mmHg')
        self.assertEqual(mt.type_name, 'Blood Pressure')

    def test_create_duplicate_metric_type(self):
        MetricTypeService.create_metric_type('Blood Pressure', 'mmHg')
        with self.assertRaises(ValidationError):
            MetricTypeService.create_metric_type('Blood Pressure', 'mmHg')