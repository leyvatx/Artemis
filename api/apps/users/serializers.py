from rest_framework import serializers
from core.serializers import RelatedAttrField
from .models import Role, User, SupervisorAssignment


class RoleSerializer(serializers.ModelSerializer):
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'users_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_users_count(self, obj):
        return obj.users.count()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Role name must be at least 2 characters long.")
        return value.strip()


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'status', 'role', 'role_name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()

    def validate_email(self, value):
        email_lower = value.lower()
        # Check for duplicates excluding the current instance
        qs = User.objects.filter(email=email_lower)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email_lower

    def validate_status(self, value):
        valid_statuses = dict(User.STATUS_CHOICES)
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {list(valid_statuses.keys())}")
        return value


class UserDetailSerializer(UserSerializer):
    """Extended serializer with related data"""
    role_details = RoleSerializer(source='role', read_only=True)
    supervisor_count = serializers.SerializerMethodField()
    officers_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['role_details', 'supervisor_count', 'officers_count']

    def get_supervisor_count(self, obj):
        return obj.supervisor_assignments.filter(end_date__isnull=True).count()

    def get_officers_count(self, obj):
        return obj.officer_assignments.filter(end_date__isnull=True).count()


class SupervisorAssignmentSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    officer_name = serializers.CharField(source='officer.name', read_only=True)
    supervisor_email = serializers.CharField(source='supervisor.email', read_only=True)
    officer_email = serializers.CharField(source='officer.email', read_only=True)

    class Meta:
        model = SupervisorAssignment
        fields = [
            'id', 'supervisor', 'officer', 'supervisor_name', 'supervisor_email',
            'officer_name', 'officer_email', 'start_date', 'end_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        supervisor = data.get('supervisor')
        officer = data.get('officer')

        if not supervisor:
            raise serializers.ValidationError({"supervisor": "Supervisor is required."})
        if not officer:
            raise serializers.ValidationError({"officer": "Officer is required."})
        if supervisor == officer:
            raise serializers.ValidationError("Supervisor and officer cannot be the same person.")

        # Check if supervisor status is Active
        if supervisor.status != 'Active':
            raise serializers.ValidationError({"supervisor": "Supervisor must have Active status."})

        # Check if officer status is Active
        if officer.status != 'Active':
            raise serializers.ValidationError({"officer": "Officer must have Active status."})

        return data
