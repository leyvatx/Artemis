import hashlib
from django.core.exceptions import ValidationError
from ..repositories.repositories import UserRepository, RoleRepository, SupervisorAssignmentRepository


class UserService:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def create_user(user_name, user_email, password, role_name=None):
        if UserRepository.get_user_by_email(user_email):
            raise ValidationError("User with this email already exists")

        hashed_password = UserService.hash_password(password)
        role = None
        if role_name:
            role = RoleRepository.get_role_by_id(role_name)  # Assuming role_name is id, or adjust

        user = UserRepository.create_user(
            user_name=user_name,
            user_email=user_email,
            user_password_hash=hashed_password,
            role=role
        )
        return user

    @staticmethod
    def authenticate_user(email, password):
        user = UserRepository.get_user_by_email(email)
        if user and user.user_password_hash == UserService.hash_password(password):
            return user
        return None

    @staticmethod
    def update_user_status(user_id, status):
        valid_statuses = ['Active', 'Inactive', 'OnLeave', 'Suspended']
        if status not in valid_statuses:
            raise ValidationError("Invalid status")
        return UserRepository.update_user(user_id, user_status=status)

    @staticmethod
    def assign_supervisor_to_officer(supervisor_id, officer_id, start_date=None, end_date=None):
        supervisor = UserRepository.get_user_by_id(supervisor_id)
        officer = UserRepository.get_user_by_id(officer_id)
        if not supervisor or not officer:
            raise ValidationError("Supervisor or officer not found")
        return SupervisorAssignmentRepository.create_assignment(
            supervisor=supervisor,
            officer=officer,
            start_date=start_date,
            end_date=end_date
        )


class RoleService:
    @staticmethod
    def create_role(role_name, description=''):
        if RoleRepository.get_all_roles().filter(role_name=role_name).exists():
            raise ValidationError("Role with this name already exists")
        return RoleRepository.create_role(role_name, description)