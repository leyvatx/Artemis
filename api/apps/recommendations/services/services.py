from ..repositories.repositories import RecommendationRepository


class RecommendationService:
    @staticmethod
    def generate_recommendation(user, message, category='', alert=None):
        return RecommendationRepository.create_recommendation(user, message, category, alert)

    @staticmethod
    def get_user_recommendations(user):
        return RecommendationRepository.get_recommendations_by_user(user)

    @staticmethod
    def get_recommendations_by_category(category):
        return Recommendation.objects.filter(category=category).order_by('-created_at')