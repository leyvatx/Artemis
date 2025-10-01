from rest_framework import viewsets
from ..models.models import Recommendation
from ..serializers.serializers import RecommendationSerializer

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
