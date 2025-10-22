from rest_framework import viewsets
from api.core.views import BaseViewSet
from .models import Role, User, SupervisorAssignment
from .serializers import RoleSerializer, UserSerializer, SupervisorAssignmentSerializer


class RoleViewSet(BaseViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SupervisorAssignmentViewSet(BaseViewSet):
    queryset = SupervisorAssignment.objects.all()
    serializer_class = SupervisorAssignmentSerializer
