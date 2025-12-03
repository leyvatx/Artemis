from django.shortcuts import render
from django.views import View
from django.contrib import messages
import requests
from django.conf import settings
from django.utils.timesince import timesince
from datetime import datetime
from ..mixins import LoginRequiredMixin
from apps.Dashboard.endpoints import ALERTS_ENDPOINTS


class AlertsListView(LoginRequiredMixin, View):
    """Vista para listar todas las alertas de los oficiales del supervisor"""
    
    template_name = 'dashboard/alerts/list.html'
    
    def _get_officer_badge(self, officer_id):
        try:
            API_BASE = 'http://165.227.21.22/api'
            officer_url = f'{API_BASE}/users/{officer_id}/'
            response = requests.get(officer_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                officer_data = data.get('data', {})
                return officer_data.get('badge_number', '')
            return ''
        except:
            return ''
    
    def _format_alert(self, alert):
        severity_to_level = {
            'CRITICAL': 'Critical',
            'HIGH': 'High',
            'MEDIUM': 'Medium',
            'LOW': 'Low'
        }
        
        level = severity_to_level.get(alert.get('severity', 'MEDIUM'), 'Medium')
        
        try:
            created = datetime.fromisoformat(alert.get('created_at', '').replace('Z', '+00:00'))
            time_ago = timesince(created)
        except:
            time_ago = 'recientemente'
        
        officer_id = alert.get('user')
        
        return {
            'id': alert.get('id'),
            'officer_id': officer_id,
            'officer_name': alert.get('user_name', 'Desconocido'),
            'officer_rank': '',
            'officer_badge': self._get_officer_badge(officer_id) if officer_id else '',
            'alert_type': alert.get('alert_type', ''),
            'level': level,
            'status': alert.get('status', 'Pending'),
            'description': alert.get('message', ''),
            'location': '',
            'created_at': alert.get('created_at', ''),
            'time_ago': time_ago,
            'severity': alert.get('severity', ''),
            'heart_rate': alert.get('heart_rate', ''),
            'stress_score': alert.get('stress_score', ''),
            'stress_level': alert.get('stress_level', ''),
            'requires_immediate_action': alert.get('requires_immediate_action', False),
            'action_required': alert.get('action_required', ''),
        }
    
    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisor_id = auth_user.get('id')
        
        if not supervisor_id:
            messages.error(request, 'No se pudo identificar el supervisor')
            return render(request, self.template_name, {'alerts': [], 'error': 'Error al identificar el usuario'})
        
        alerts = []
        error = None
        
        try:
            API_URL = ALERTS_ENDPOINTS['LIST']
            response = requests.get(API_URL, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                raw_alerts = data.get('data', []) if isinstance(data, dict) else data
                alerts = [self._format_alert(alert) for alert in raw_alerts]  
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
