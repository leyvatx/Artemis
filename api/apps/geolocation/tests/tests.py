import pytest
from django.test import TestCase
from ..models.models import GeoLocation
from ..serializers.serializers import GeoLocationSerializer
from ..services.services import GeoLocationService
from apps.users.models import User


class GeoLocationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_create_geolocation(self):
        geo = GeoLocation.objects.create(
            user=self.user,
            location='40.7128,-74.0060'
        )
        self.assertEqual(geo.location, '40.7128,-74.0060')
        self.assertEqual(str(geo), 'Test User at 40.7128,-74.0060')


class GeoLocationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_serialize_geolocation(self):
        geo = GeoLocation.objects.create(user=self.user, location='0,0')
        serializer = GeoLocationSerializer(geo)
        self.assertEqual(serializer.data['location'], '0,0')


class GeoLocationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_track_user_location(self):
        geo = GeoLocationService.track_user_location(self.user, '10,20')
        self.assertEqual(geo.location, '10,20')

    def test_get_user_location_history(self):
        GeoLocationService.track_user_location(self.user, '10,20')
        history = GeoLocationService.get_user_location_history(self.user)
        self.assertEqual(len(history), 1)