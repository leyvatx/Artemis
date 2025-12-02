from core.views import BaseViewSet
from .models import Event
from .serializers import EventSerializer
from apps.users.models import SupervisorAssignment
from rest_framework.permissions import IsAuthenticated


class EventViewSet(BaseViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrar eventos según el rol del usuario:
        - Supervisores: ven eventos de sus oficiales asignados
        - Oficiales: ven solo sus propios eventos
        """
        user = self.request.user
        
        # Si es oficial, solo ve sus propios eventos
        if user.role and user.role.name == 'officer':
            return Event.objects.filter(user=user).order_by('-created_at')
        
        # Si es supervisor, ve eventos de sus oficiales asignados
        if user.role and user.role.name == 'supervisor':
            assigned_officers = SupervisorAssignment.objects.filter(
                supervisor=user,
                end_date__isnull=True
            ).values_list('officer_id', flat=True)
            
            return Event.objects.filter(user_id__in=assigned_officers).order_by('-created_at')
        
        # Por defecto, no devolver nada
        return Event.objects.none()