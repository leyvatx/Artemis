from rest_framework import serializers
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
    picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'badge_number', 'rank', 'picture', 'role', 'status']
        read_only_fields = ['id']

    def validate_status(self, value):
        allowed = [choice[0] for choice in User.STATUS_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(allowed)}")
        return value

    def get_picture(self, obj):
        """Return absolute URL to the picture if possible, else relative URL or None."""
        if not obj or not getattr(obj, 'picture', None):
            return None
        try:
            url = obj.picture.url
        except Exception:
            return None
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request:
            return request.build_absolute_uri(url)
        return url


class UserSummarySerializer(serializers.ModelSerializer):
    """Compact user representation for nested responses (no timestamps)."""
    picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'badge_number', 'rank', 'picture', 'status']

    def get_picture(self, obj):
        """Return absolute URL to the picture if possible, else relative URL or None."""
        if not obj or not getattr(obj, 'picture', None):
            return None
        try:
            url = obj.picture.url
        except Exception:
            return None
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request:
            return request.build_absolute_uri(url)
        return url

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()

    def validate_email(self, value):
        email_lower = value.lower()
        qs = User.objects.filter(email=email_lower)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email_lower

    def validate_badge_number(self, value):
        if value:
            qs = User.objects.filter(badge_number=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("A user with this badge number already exists.")
        return value



class UserDetailSerializer(UserSerializer):
    """Extended serializer with related data"""
    role_details = RoleSerializer(source='role', read_only=True)
    supervisor_count = serializers.SerializerMethodField()
    officers_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['role_details', 'supervisor_count', 'officers_count', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_supervisor_count(self, obj):
        return obj.supervisor_assignments.filter(end_date__isnull=True).count()

    def get_officers_count(self, obj):
        return obj.officer_assignments.filter(end_date__isnull=True).count()


class OfficerSerializer(serializers.ModelSerializer):
    """Clean serializer for officers under a supervisor"""
    picture = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'badge_number', 'rank', 'picture', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_picture(self, obj):
        if not obj or not getattr(obj, 'picture', None):
            return None
        try:
            url = obj.picture.url
        except Exception:
            return None
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request:
            return request.build_absolute_uri(url)
        return url


class SupervisorSerializer(serializers.ModelSerializer):
    """Clean serializer for supervisors"""
    picture = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'badge_number', 'rank', 'picture', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_picture(self, obj):
        if not obj or not getattr(obj, 'picture', None):
            return None
        try:
            url = obj.picture.url
        except Exception:
            return None
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request:
            return request.build_absolute_uri(url)
        return url


class SupervisorAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating assignments. Keep supervisor/officer as IDs only."""

    class Meta:
        model = SupervisorAssignment
        fields = [
            'id', 'supervisor', 'officer', 'start_date', 'end_date', 'notes',
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

        if supervisor.status != 'Active':
            raise serializers.ValidationError({"supervisor": "Supervisor must have Active status."})

        if officer.status != 'Active':
            raise serializers.ValidationError({"officer": "Officer must have Active status."})

        return data


class CleanSupervisorAssignmentSerializer(serializers.ModelSerializer):
    """Clean serializer for supervisor assignments with nested objects"""
    supervisor = UserSummarySerializer(read_only=True)
    officer = UserSummarySerializer(read_only=True)

    class Meta:
        model = SupervisorAssignment
        fields = [
            'id', 'supervisor', 'officer', 'start_date', 'end_date', 'notes'
        ]
        read_only_fields = ['id']
