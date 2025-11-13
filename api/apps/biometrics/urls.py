from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BPMViewSet

router = DefaultRouter()
router.register(r'', BPMViewSet, basename='bpm')

urlpatterns = [
    path('', include(router.urls)),
]