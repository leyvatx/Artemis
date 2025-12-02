from core.views import BaseViewSet
from .models import GeoLocation
from .serializers import GeoLocationSerializer
from apps.users.models import SupervisorAssignment
from rest_framework.permissions import IsAuthenticated


class GeoLocationViewSet(BaseViewSet):
    queryset = GeoLocation.objects.all()
    serializer_class = GeoLocationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrar geolocalización según el rol del usuario:
        - Supervisores: ven geolocalización de sus oficiales asignados
        - Oficiales: ven solo su propia geolocalización
        """
        user = self.request.user
        
        # Si es oficial, solo ve su propia geolocalización
        if user.role and user.role.name == 'officer':
            return GeoLocation.objects.filter(user=user).order_by('-created_at')
        
        # Si es supervisor, ve geolocalización de sus oficiales asignados
        if user.role and user.role.name == 'supervisor':
            assigned_officers = SupervisorAssignment.objects.filter(
                supervisor=user,
                end_date__isnull=True
            ).values_list('officer_id', flat=True)
            
            return GeoLocation.objects.filter(user_id__in=assigned_officers).order_by('-created_at')
        
        # Por defecto, no devolver nada
        return GeoLocation.objects.none()