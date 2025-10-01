from celery import shared_task
from .services import EventService


@shared_task
def process_event_logs():
    # Placeholder for processing event logs
    print("Processing event logs")
    return True


@shared_task
def clean_old_events(days=90):
    # Placeholder for cleaning old events
    print(f"Cleaning events older than {days} days")
    return True