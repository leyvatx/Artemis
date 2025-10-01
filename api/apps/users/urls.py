from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, UserViewSet, SupervisorAssignmentViewSet

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)
router.register(r'supervisor-assignments', SupervisorAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]