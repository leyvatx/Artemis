from api.core.views import BaseViewSet
from .models import Recommendation
from .serializers import RecommendationSerializer


class RecommendationViewSet(BaseViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer