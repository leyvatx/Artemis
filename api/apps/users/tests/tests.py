import pytest
from django.test import TestCase
from ..models.models import Role, User, SupervisorAssignment
from ..serializers.serializers import RoleSerializer, UserSerializer, SupervisorAssignmentSerializer
from ..services.services import UserService, RoleService


class RoleModelTest(TestCase):
    def test_create_role(self):
        role = Role.objects.create(role_name='Admin', description='Administrator')
        self.assertEqual(role.role_name, 'Admin')
        self.assertEqual(str(role), 'Admin')


class UserModelTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(role_name='User')

    def test_create_user(self):
        user = User.objects.create(
            user_name='John Doe',
            user_email='john@example.com',
            user_password_hash='hashedpass'
        )
        self.assertEqual(user.user_name, 'John Doe')
        self.assertEqual(str(user), 'John Doe')


class SupervisorAssignmentModelTest(TestCase):
    def setUp(self):
        self.supervisor = User.objects.create(
            user_name='Supervisor',
            user_email='supervisor@example.com',
            user_password_hash='hash'
        )
        self.officer = User.objects.create(
            user_name='Officer',
            user_email='officer@example.com',
            user_password_hash='hash'
        )

    def test_create_assignment(self):
        assignment = SupervisorAssignment.objects.create(
            supervisor=self.supervisor,
            officer=self.officer
        )
        self.assertEqual(assignment.supervisor, self.supervisor)
        self.assertEqual(str(assignment), 'Supervisor -> Officer')


class RoleSerializerTest(TestCase):
    def test_serialize_role(self):
        role = Role.objects.create(role_name='Test Role')
        serializer = RoleSerializer(role)
        self.assertEqual(serializer.data['role_name'], 'Test Role')


class UserServiceTest(TestCase):
    def test_hash_password(self):
        hashed = UserService.hash_password('password')
        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 64)  # SHA256 hex length

    def test_create_user(self):
        user = UserService.create_user('Test User', 'test@example.com', 'password')
        self.assertEqual(user.user_name, 'Test User')
        self.assertEqual(user.user_email, 'test@example.com')

    def test_create_duplicate_user(self):
        UserService.create_user('Test User', 'test@example.com', 'password')
        with self.assertRaises(ValidationError):
            UserService.create_user('Another User', 'test@example.com', 'password')


class RoleServiceTest(TestCase):
    def test_create_role(self):
        role = RoleService.create_role('New Role', 'Description')
        self.assertEqual(role.role_name, 'New Role')

    def test_create_duplicate_role(self):
        RoleService.create_role('New Role', 'Description')
        with self.assertRaises(ValidationError):
            RoleService.create_role('New Role', 'Another Description')