from celery import shared_task
from .services import RecommendationService


@shared_task
def generate_daily_recommendations():
    # Placeholder for generating daily recommendations
    print("Generating daily recommendations")
    return True


@shared_task
def clean_old_recommendations(days=30):
    # Placeholder for cleaning old recommendations
    print(f"Cleaning recommendations older than {days} days")
    return True