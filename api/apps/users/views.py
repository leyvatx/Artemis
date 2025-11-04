from rest_framework import viewsets
from core.views import BaseViewSet
from .models import Role, User, SupervisorAssignment
from .serializers import RoleSerializer, UserSerializer, SupervisorAssignmentSerializer
from apps.events import EventLogger  # ← NUEVO: Para registrar eventos


class RoleViewSet(BaseViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear un usuario y registrar evento"""
        response = super().create(request, *args, **kwargs)
        
        # ← NUEVO: Registrar evento de usuario creado
        user_data = response.data
        EventLogger.log_event(
            user=request.user,
            title="User Created",
            category="User_Created",
            description=f"Nuevo usuario: {user_data.get('email', 'unknown')}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar un usuario y registrar evento"""
        response = super().destroy(request, *args, **kwargs)
        
        # ← NUEVO: Registrar evento de usuario eliminado
        EventLogger.log_event(
            user=request.user,
            title="User Deleted",
            category="User_Deleted",
            description="Usuario eliminado del sistema",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return response


class SupervisorAssignmentViewSet(BaseViewSet):
    queryset = SupervisorAssignment.objects.all()
    serializer_class = SupervisorAssignmentSerializer
