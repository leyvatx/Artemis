from rest_framework import serializers
from .models import Role, User, SupervisorAssignment

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = '__all__'

class SupervisorAssignmentSerializer(serializers.ModelSerializer):
    supervisor = UserSerializer(read_only=True)
    officer = UserSerializer(read_only=True)

    class Meta:
        model = SupervisorAssignment
        fields = '__all__'