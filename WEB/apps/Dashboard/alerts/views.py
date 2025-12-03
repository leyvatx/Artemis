from django.shortcuts import render
from django.views import View
from django.contrib import messages
import requests
from django.conf import settings
from ..mixins import LoginRequiredMixin
from apps.Dashboard.endpoints import BIOMETRICS_ENDPOINTS


class AlertsListView(LoginRequiredMixin, View):
    """Vista para listar todas las alertas de los oficiales del supervisor"""
    
    template_name = 'dashboard/alerts/list.html'
    
    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisor_id = auth_user.get('id')
        
        if not supervisor_id:
            messages.error(request, 'No se pudo identificar el supervisor')
            return render(request, self.template_name, {'alerts': [], 'error': 'Error al identificar el usuario'})
        
        alerts = []
        error = None
        
        try:
            API_URL = BIOMETRICS_ENDPOINTS['LIST']
            response = requests.get(API_URL, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('data', [])
            elif response.status_code == 404:
                error = "No se encontró el supervisor o no tiene oficiales asignados"
            else:
                error = f"Error al cargar las alertas (Código: {response.status_code})"
                
        except requests.exceptions.Timeout:
            error = "El servidor tardó demasiado en responder"
        except requests.exceptions.ConnectionError:
            error = "No se pudo conectar con el servidor de API"
        except Exception as e:
            error = f"Error inesperado: {str(e)}"
        
        context = {
            'alerts': alerts,
            'error': error,
            'alerts_count': len(alerts),
            'auth_user': auth_user,
            'supervisor_id': supervisor_id
        }
        
        return render(request, self.template_name, context)
