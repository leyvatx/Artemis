import uuid
from django.utils import timezone


def generate_unique_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())


def get_current_timestamp():
    """Get current timestamp."""
    return timezone.now()