from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertTypeViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'alert-types', AlertTypeViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
]