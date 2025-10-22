from rest_framework import serializers
from api.core.serializers import RelatedAttrField
from .models import Role, User, SupervisorAssignment


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class SupervisorAssignmentSerializer(serializers.ModelSerializer):
    supervisor_name = RelatedAttrField('supervisor.name')
    officer_name = RelatedAttrField('officer.name')

    class Meta:
        model = SupervisorAssignment
        fields = ['id', 'supervisor', 'officer', 'supervisor_name', 'officer_name', 'start_date', 'end_date']

    def validate(self, data):
        if not data.get('supervisor'):
            raise serializers.ValidationError("Supervisor is required")
        if not data.get('officer'):
            raise serializers.ValidationError("Officer is required")
        if data.get('supervisor') == data.get('officer'):
            raise serializers.ValidationError("Supervisor and officer cannot be the same person")
        return data