from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GeoLocationViewSet

router = DefaultRouter()
router.register(r'', GeoLocationViewSet, basename='geolocation')

urlpatterns = [
    path('', include(router.urls)),
]