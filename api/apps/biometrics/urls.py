from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BPMViewSet, MLPredictionViewSet, MLAlertViewSet

router = DefaultRouter()
router.register(r'bpm', BPMViewSet, basename='bpm')
router.register(r'predictions', MLPredictionViewSet, basename='ml-prediction')
router.register(r'alerts', MLAlertViewSet, basename='ml-alert')

urlpatterns = [
    path('', include(router.urls)),
]