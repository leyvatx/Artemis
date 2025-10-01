from django.db import models
from ..models.models import Role, User, SupervisorAssignment


class RoleRepository:
    @staticmethod
    def get_all_roles():
        return Role.objects.all()

    @staticmethod
    def get_role_by_id(role_id):
        try:
            return Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return None

    @staticmethod
    def create_role(role_name, description=''):
        return Role.objects.create(role_name=role_name, description=description)

    @staticmethod
    def update_role(role_id, **kwargs):
        role = RoleRepository.get_role_by_id(role_id)
        if role:
            for key, value in kwargs.items():
                setattr(role, key, value)
            role.save()
            return role
        return None

    @staticmethod
    def delete_role(role_id):
        role = RoleRepository.get_role_by_id(role_id)
        if role:
            role.delete()
            return True
        return False


class UserRepository:
    @staticmethod
    def get_all_users():
        return User.objects.all()

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(user_email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def create_user(user_name, user_email, user_password_hash, role=None, user_status='Active'):
        return User.objects.create(
            user_name=user_name,
            user_email=user_email,
            user_password_hash=user_password_hash,
            role=role,
            user_status=user_status
        )

    @staticmethod
    def update_user(user_id, **kwargs):
        user = UserRepository.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            user.save()
            return user
        return None

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_user_by_id(user_id)
        if user:
            user.delete()
            return True
        return False


class SupervisorAssignmentRepository:
    @staticmethod
    def get_all_assignments():
        return SupervisorAssignment.objects.all()

    @staticmethod
    def get_assignment_by_id(assignment_id):
        try:
            return SupervisorAssignment.objects.get(pk=assignment_id)
        except SupervisorAssignment.DoesNotExist:
            return None

    @staticmethod
    def create_assignment(supervisor, officer, start_date=None, end_date=None):
        return SupervisorAssignment.objects.create(
            supervisor=supervisor,
            officer=officer,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def update_assignment(assignment_id, **kwargs):
        assignment = SupervisorAssignmentRepository.get_assignment_by_id(assignment_id)
        if assignment:
            for key, value in kwargs.items():
                setattr(assignment, key, value)
            assignment.save()
            return assignment
        return None

    @staticmethod
    def delete_assignment(assignment_id):
        assignment = SupervisorAssignmentRepository.get_assignment_by_id(assignment_id)
        if assignment:
            assignment.delete()
            return True
        return False