from ..models.models import Recommendation


class RecommendationRepository:
    @staticmethod
    def get_all_recommendations():
        return Recommendation.objects.all()

    @staticmethod
    def get_recommendation_by_id(recommendation_id):
        try:
            return Recommendation.objects.get(pk=recommendation_id)
        except Recommendation.DoesNotExist:
            return None

    @staticmethod
    def get_recommendations_by_user(user):
        return Recommendation.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def create_recommendation(user, message, category='', alert=None):
        return Recommendation.objects.create(
            user=user,
            alert=alert,
            message=message,
            category=category
        )

    @staticmethod
    def update_recommendation(recommendation_id, **kwargs):
        recommendation = RecommendationRepository.get_recommendation_by_id(recommendation_id)
        if recommendation:
            for key, value in kwargs.items():
                setattr(recommendation, key, value)
            recommendation.save()
            return recommendation
        return None

    @staticmethod
    def delete_recommendation(recommendation_id):
        recommendation = RecommendationRepository.get_recommendation_by_id(recommendation_id)
        if recommendation:
            recommendation.delete()
            return True
        return False