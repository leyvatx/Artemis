from celery import shared_task
from .services import BiometricService


@shared_task
def process_biometric_alerts():
    # Placeholder for processing biometric data and generating alerts
    print("Processing biometric alerts")
    return True


@shared_task
def clean_old_biometric_data(days=30):
    # Placeholder for cleaning old biometric data
    print(f"Cleaning biometric data older than {days} days")
    return True