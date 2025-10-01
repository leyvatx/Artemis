from celery import shared_task
from .services import GeoLocationService


@shared_task
def process_location_alerts():
    # Placeholder for processing location data and generating alerts
    print("Processing location alerts")
    return True


@shared_task
def clean_old_location_data(days=30):
    # Placeholder for cleaning old location data
    print(f"Cleaning location data older than {days} days")
    return True