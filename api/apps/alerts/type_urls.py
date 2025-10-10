from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertTypeViewSet

router = DefaultRouter()
router.register(r'', AlertTypeViewSet, basename='alert-type')

urlpatterns = [
    path('', include(router.urls)),
]