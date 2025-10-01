import pytest
from django.test import TestCase
from ..models.models import Recommendation
from ..serializers.serializers import RecommendationSerializer
from ..services.services import RecommendationService
from apps.users.models import User


class RecommendationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_create_recommendation(self):
        rec = Recommendation.objects.create(
            user=self.user,
            message='Test recommendation'
        )
        self.assertEqual(rec.message, 'Test recommendation')
        self.assertEqual(str(rec), 'Test recommendation')


class RecommendationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_serialize_recommendation(self):
        rec = Recommendation.objects.create(user=self.user, message='Test')
        serializer = RecommendationSerializer(rec)
        self.assertEqual(serializer.data['message'], 'Test')


class RecommendationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            user_name='Test User',
            user_email='test@example.com',
            user_password_hash='hash'
        )

    def test_generate_recommendation(self):
        rec = RecommendationService.generate_recommendation(self.user, 'Take a break')
        self.assertEqual(rec.message, 'Take a break')

    def test_get_user_recommendations(self):
        RecommendationService.generate_recommendation(self.user, 'Take a break')
        recs = RecommendationService.get_user_recommendations(self.user)
        self.assertEqual(len(recs), 1)