from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.views import BaseViewSet
from .models import Recommendation
from .serializers import RecommendationSerializer


class RecommendationViewSet(BaseViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    
    def get_queryset(self):
        """Filtrar por officer_id si se proporciona en query params"""
        queryset = Recommendation.objects.all().order_by('-created_at')
        officer_id = self.request.query_params.get('officer', None)
        if officer_id:
            queryset = queryset.filter(user_id=officer_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Marcar una recomendación como reconocida"""
        try:
            recommendation = self.get_object()
            recommendation.status = 'Reconocida'
            recommendation.acknowledged_at = timezone.now()
            recommendation.save()
            
            serializer = self.get_serializer(recommendation)
            return Response({
                'success': True,
                'message': 'Recomendación reconocida correctamente',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Marcar una recomendación como resuelta con justificación"""
        try:
            recommendation = self.get_object()
            
            resolution_notes = request.data.get('resolution_notes', '')
            if not resolution_notes:
                return Response({
                    'success': False,
                    'error': 'Se requiere una justificación para resolver la recomendación'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            recommendation.status = 'Resuelta'
            recommendation.resolved_at = timezone.now()
            recommendation.resolution_notes = resolution_notes
            recommendation.is_active = False
            
            # Si viene un user_id en la request, usarlo
            resolved_by_id = request.data.get('resolved_by')
            if resolved_by_id:
                from apps.users.models import User
                try:
                    recommendation.resolved_by = User.objects.get(pk=resolved_by_id)
                except User.DoesNotExist:
                    pass
            
            recommendation.save()
            
            serializer = self.get_serializer(recommendation)
            return Response({
                'success': True,
                'message': 'Recomendación resuelta correctamente',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)