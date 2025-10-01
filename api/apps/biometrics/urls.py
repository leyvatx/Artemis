from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetricTypeViewSet, BiometricViewSet

router = DefaultRouter()
router.register(r'metric-types', MetricTypeViewSet)
router.register(r'biometrics', BiometricViewSet)

urlpatterns = [
    path('', include(router.urls)),
]