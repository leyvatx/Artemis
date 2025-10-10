from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupervisorAssignmentViewSet

router = DefaultRouter()
router.register(r'', SupervisorAssignmentViewSet, basename='supervisor')

urlpatterns = [
    path('', include(router.urls)),
]