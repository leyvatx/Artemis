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
    role_id = serializers.PrimaryKeyRelatedField(
        source='role',
        queryset=Role.objects.all(),
        required=False,
        allow_null=True
    )

    picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'badge_number',
            'rank',
            'picture',
            'role_id',
            'status'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if instance.picture and request:
            rep['picture'] = request.build_absolute_uri(instance.picture.url)
        elif instance.picture:
            rep['picture'] = instance.picture.url
        return rep

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value

    def validate_email(self, value):
        email_lower = value.strip().lower()
        qs = User.objects.filter(email=email_lower)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email_lower

    def validate_badge_number(self, value):
        if value:
            value = value.strip()
            qs = User.objects.filter(badge_number=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("A user with this badge number already exists.")
        return value

    def validate_status(self, value):
        valid_statuses = dict(User.STATUS_CHOICES)
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Choose from: {list(valid_statuses.keys())}"
            )
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
    picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'badge_number', 'rank', 'picture', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if instance.picture and request:
            rep['picture'] = request.build_absolute_uri(instance.picture.url)
        elif instance.picture:
            rep['picture'] = instance.picture.url
        return rep


class SupervisorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'badge_number',
            'rank',
            'picture',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


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


        return data


class CleanSupervisorAssignmentSerializer(serializers.ModelSerializer):
    """Clean serializer for supervisor assignments with nested objects"""
    supervisor = SupervisorSerializer(read_only=True)
    officer = OfficerSerializer(read_only=True)

    class Meta:
        model = SupervisorAssignment
        fields = [
            'id', 'supervisor', 'officer', 'start_date', 'end_date', 'notes'
        ]
        read_only_fields = ['id']


class AlertDetailSerializer(serializers.Serializer):
    """Serializer for alerts with detailed officer information"""
    id = serializers.IntegerField()
    officer_id = serializers.IntegerField(source='user.id')
    officer_name = serializers.CharField(source='user.name')
    officer_email = serializers.CharField(source='user.email')
    officer_badge = serializers.CharField(source='user.badge_number')
    officer_rank = serializers.CharField(source='user.rank')
    alert_type = serializers.CharField(source='type.name')
    level = serializers.CharField()
    status = serializers.CharField()
    description = serializers.CharField()
    location = serializers.CharField()
    created_at = serializers.DateTimeField()
    acknowledged_at = serializers.DateTimeField(allow_null=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.name', allow_null=True)
    resolution_notes = serializers.CharField()
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Agregar información adicional
        ret['time_ago'] = self._get_time_ago(instance.created_at)
        ret['is_critical'] = instance.level in ['High', 'Critical']
        return ret
    
    def _get_time_ago(self, datetime):
        from django.utils import timezone
        now = timezone.now()
        diff = now - datetime
        
        if diff.days > 0:
            return f"Hace {diff.days}d"
        elif diff.seconds > 3600:
            return f"Hace {diff.seconds // 3600}h"
        elif diff.seconds > 60:
            return f"Hace {diff.seconds // 60}m"
        else:
            return "Hace poco"