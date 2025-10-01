import pytest
from django.test import TestCase
from ..models.models import Event
from ..serializers.serializers import EventSerializer
from ..services.services import EventService
from apps.users.models import User


class EventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_create_event(self):
        event = Event.objects.create(
            user=self.user,
            title='Test Event',
            description='Description',
            category='Test'
        )
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(str(event), 'Test Event')


class EventSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_serialize_event(self):
        event = Event.objects.create(user=self.user, title='Test')
        serializer = EventSerializer(event)
        self.assertEqual(serializer.data['title'], 'Test')


class EventServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_log_event(self):
        event = EventService.log_event(self.user, 'Login', 'User logged in')
        self.assertEqual(event.title, 'Login')

    def test_get_user_events(self):
        EventService.log_event(self.user, 'Login')
        events = EventService.get_user_events(self.user)
        self.assertEqual(len(events), 1)