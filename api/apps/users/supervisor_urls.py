from django.urls import path, include
from .views import supervisor_alerts_view, supervisor_officers_view, supervisor_statistics_view

from rest_framework.routers import DefaultRouter
from .views import SupervisorAssignmentViewSet, SupervisorViewSet

router = DefaultRouter()
router.register(r'assignments', SupervisorAssignmentViewSet, basename='supervisor-assignment')
router.register(r'', SupervisorViewSet, basename='supervisor')

urlpatterns = [
    path('<int:supervisor_id>/alerts/', supervisor_alerts_view, name='supervisor-alerts'),
    path('<int:supervisor_id>/officers/', supervisor_officers_view, name='supervisor-officers'),
    path('<int:supervisor_id>/statistics/', supervisor_statistics_view, name='supervisor-statistics'),

    path('', include(router.urls)),
]