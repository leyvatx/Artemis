from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, test_endpoint

router = DefaultRouter()
router.register(r'', AlertViewSet, basename='alert')

urlpatterns = [
    path('test/', test_endpoint),
    path('', include(router.urls)),
]