from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupervisorAssignmentViewSet, SupervisorViewSet

router = DefaultRouter()
router.register(r'assignments', SupervisorAssignmentViewSet, basename='supervisor-assignment')
router.register(r'', SupervisorViewSet, basename='supervisor')

urlpatterns = [
    path('', include(router.urls)),
]