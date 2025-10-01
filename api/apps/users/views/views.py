from rest_framework import viewsets
from ..models.models import Role, User, SupervisorAssignment
from ..serializers.serializers import RoleSerializer, UserSerializer, SupervisorAssignmentSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SupervisorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = SupervisorAssignment.objects.all()
    serializer_class = SupervisorAssignmentSerializer
