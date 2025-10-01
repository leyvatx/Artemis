from celery import shared_task
from .services import ReportService


@shared_task
def generate_monthly_reports():
    # Placeholder for generating monthly reports
    print("Generating monthly reports")
    return True


@shared_task
def clean_old_reports(days=365):
    # Placeholder for cleaning old reports
    print(f"Cleaning reports older than {days} days")
    return True