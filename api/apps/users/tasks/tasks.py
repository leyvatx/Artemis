from celery import shared_task
from ..services.services import UserService


@shared_task
def send_welcome_email(user_id):
    # Placeholder for sending welcome email
    user = UserService.get_user_by_id(user_id)
    if user:
        # Send email logic here
        print(f"Sending welcome email to {user.user_email}")
        return True
    return False


@shared_task
def deactivate_inactive_users():
    # Placeholder for deactivating users who haven't logged in for a while
    # This would require login tracking, but for now placeholder
    print("Deactivating inactive users")
    return True