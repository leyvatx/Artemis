from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetricTypeViewSet

router = DefaultRouter()
router.register(r'', MetricTypeViewSet, basename='metric-type')

urlpatterns = [
    path('', include(router.urls)),
]