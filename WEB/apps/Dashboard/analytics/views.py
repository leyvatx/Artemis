
# -- VIEWS ------------------------------------------------------------------- #

from django.views import View
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import logging

from ..mixins import LoginRequiredMixin
from ..endpoints import ANALYTICS_ENDPOINTS, OFFICERS_ENDPOINTS

# ---------------------------------------------------------------------------- #

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #

''' CLASE: Vista principal de Analytics '''
class AnalyticsView(LoginRequiredMixin, View):
    template_name = 'dashboard/analytics/analytics.html'

    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisor_id = auth_user.get('id')
        
        # Obtener lista de oficiales para el selector
        officers_url = OFFICERS_ENDPOINTS['LIST'].format(id=supervisor_id)
        
        try:
            response = requests.get(officers_url)
            data = response.json() if response.status_code == 200 else {}
            officers = data.get('officers', [])
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching officers: {e}')
            officers = []
        
        context = {
            'officers': officers,
            'section': 'analytics'
        }
        
        return render(request, self.template_name, context)

# ---------------------------------------------------------------------------- #

''' CLASE: Historical Data View '''
class HistoricalDataView(LoginRequiredMixin, View):
    template_name = 'dashboard/analytics/historical_data.html'
    TABLE_RECORDS_PER_PAGE = 12  # 12 registros por página para la tabla
    CHART_MAX_POINTS = 50  # 50 puntos para la gráfica

    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisor_id = auth_user.get('id')
        officer_id = request.GET.get('officer_id')
        page = int(request.GET.get('page', 1))
        
        # Obtener lista de oficiales
        officers_url = OFFICERS_ENDPOINTS['LIST'].format(id=supervisor_id)
        
        try:
            response = requests.get(officers_url)
            data = response.json() if response.status_code == 200 else {}
            officers = data.get('officers', [])
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching officers: {e}')
            officers = []
        
        # Si se seleccionó un oficial, obtener sus datos históricos
        historical_data = []
        chart_data = []
        avg_bpm = 0
        max_bpm = 0
        min_bpm = 0
        total_records = 0
        total_pages = 1
        
        if officer_id:
            bpm_url = ANALYTICS_ENDPOINTS['HISTORICAL_BPM'].format(id=officer_id)
            
            try:
                response = requests.get(bpm_url)
                if response.status_code == 200:
                    api_response = response.json()
                    # La API devuelve {"success": true, "data": [...]}
                    all_data = api_response.get('data', [])
                    total_records = len(all_data)
                    
                    # Calcular estadísticas
                    if all_data:
                        bpm_values = [d.get('value', 0) for d in all_data if d.get('value')]
                        if bpm_values:
                            avg_bpm = round(sum(bpm_values) / len(bpm_values), 1)
                            max_bpm = max(bpm_values)
                            min_bpm = min(bpm_values)
                    
                    # Para la gráfica: últimas 50 lecturas (ordenadas de antigua a nueva)
                    latest_for_chart = all_data[:self.CHART_MAX_POINTS]
                    chart_data = list(reversed(latest_for_chart))
                    
                    # Paginación para la tabla (12 por página)
                    total_pages = (total_records + self.TABLE_RECORDS_PER_PAGE - 1) // self.TABLE_RECORDS_PER_PAGE
                    start_idx = (page - 1) * self.TABLE_RECORDS_PER_PAGE
                    end_idx = start_idx + self.TABLE_RECORDS_PER_PAGE
                    historical_data = all_data[start_idx:end_idx]
                    
            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching historical data: {e}')
                messages.error(request, 'Error al obtener datos históricos.')
        
        # Número inicial para la numeración de la tabla (ej: página 2 empieza en 13)
        start_number = (page - 1) * self.TABLE_RECORDS_PER_PAGE
        
        # Generar rango de páginas estilo Google (1 2 3 ... 8 9 10)
        page_range = self._get_page_range(page, total_pages)
        
        context = {
            'officers': officers,
            'selected_officer_id': officer_id,
            'historical_data': historical_data,
            'chart_data': chart_data,  # Últimos 50 datos para la gráfica
            'avg_bpm': avg_bpm,
            'max_bpm': max_bpm,
            'min_bpm': min_bpm,
            'total_records': total_records,
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'start_number': start_number,  # Para numerar registros
            'page_range': page_range,  # Para paginación estilo Google
            'section': 'analytics'
        }
        
        return render(request, self.template_name, context)
    
    def _get_page_range(self, current_page, total_pages, window=2):
        """Genera rango de páginas estilo Google: 1 2 3 ... 8 9 10"""
        if total_pages <= 7:
            return list(range(1, total_pages + 1))
        
        pages = []
        
        # Siempre mostrar página 1
        pages.append(1)
        
        # Calcular rango alrededor de la página actual
        start = max(2, current_page - window)
        end = min(total_pages - 1, current_page + window)
        
        # Agregar ... si hay hueco después del 1
        if start > 2:
            pages.append('...')
        
        # Agregar páginas del rango
        for p in range(start, end + 1):
            pages.append(p)
        
        # Agregar ... si hay hueco antes de la última
        if end < total_pages - 1:
            pages.append('...')
        
        # Siempre mostrar última página
        pages.append(total_pages)
        
        return pages

# ---------------------------------------------------------------------------- #

''' CLASE: Anomaly Detection View '''
class AnomalyDetectionView(LoginRequiredMixin, View):
    template_name = 'dashboard/analytics/anomaly_detection.html'

    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisor_id = auth_user.get('id')
        officer_id = request.GET.get('officer_id')
        
        # Obtener lista de oficiales
        officers_url = OFFICERS_ENDPOINTS['LIST'].format(id=supervisor_id)
        
        try:
            response = requests.get(officers_url)
            data = response.json() if response.status_code == 200 else {}
            officers = data.get('officers', [])
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching officers: {e}')
            officers = []
        
        # Obtener anomalías detectadas - SOLO si se seleccionó un oficial
        anomalies = []
        if officer_id:
            anomaly_url = ANALYTICS_ENDPOINTS['ANOMALY_BY_OFFICER'].format(id=officer_id)
            
            try:
                response = requests.get(anomaly_url)
                if response.status_code == 200:
                    api_response = response.json()
                    # La API devuelve {"success": true, "data": [...]}
                    anomalies = api_response.get('data', [])
                
                # Formatear datos para mejor visualización
                for anomaly in anomalies:
                    # Formatear fecha
                    if anomaly.get('created_at'):
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(anomaly['created_at'].replace('Z', '+00:00'))
                            anomaly['created_at_formatted'] = dt.strftime('%d/%m/%Y %H:%M')
                        except:
                            anomaly['created_at_formatted'] = anomaly['created_at']
                    
                    # Limitar decimales del stress_score
                    if anomaly.get('stress_score') is not None:
                        anomaly['stress_score_formatted'] = round(float(anomaly['stress_score']), 2)
                    else:
                        anomaly['stress_score_formatted'] = 0
                        
            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching anomalies: {e}')
                messages.error(request, 'Error al obtener detección de anomalías.')
        
        # Calcular estadísticas
        total_alerts = len(anomalies)
        pending_count = sum(1 for a in anomalies if a.get('status') == 'Pending')
        resolved_count = sum(1 for a in anomalies if a.get('status') == 'Resolved')
        
        context = {
            'officers': officers,
            'selected_officer_id': officer_id,
            'anomalies': anomalies,
            'total_alerts': total_alerts,
            'pending_count': pending_count,
            'resolved_count': resolved_count,
            'section': 'analytics'
        }
        
        return render(request, self.template_name, context)

# ---------------------------------------------------------------------------- #

''' CLASE: Anomaly Action View (Acknowledge/Resolve) '''
class AnomalyActionView(LoginRequiredMixin, View):
    
    def post(self, request, alert_id, action):
        # Determinar el endpoint según la acción
        if action == 'acknowledge':
            action_url = f"{ANALYTICS_ENDPOINTS['ANOMALY_DETECTION']}{alert_id}/acknowledge/"
        elif action == 'resolve':
            action_url = f"{ANALYTICS_ENDPOINTS['ANOMALY_DETECTION']}{alert_id}/resolve/"
        else:
            messages.error(request, 'Acción no válida.')
            return redirect('dashboard:AnomalyDetection')
        
        try:
            response = requests.post(action_url)
            if response.status_code == 200:
                if action == 'acknowledge':
                    messages.success(request, 'Alerta reconocida correctamente.')
                else:
                    messages.success(request, 'Alerta marcada como resuelta.')
            else:
                messages.error(request, f'Error al procesar la acción: {response.status_code}')
        except requests.exceptions.RequestException as e:
            logger.error(f'Error processing alert action: {e}')
            messages.error(request, 'Error de conexión al procesar la acción.')
        
        # Redirigir de vuelta a la página de anomalías
        return redirect('dashboard:AnomalyDetection')

# ---------------------------------------------------------------------------- #

''' CLASE: ML Predictions View '''
class MLPredictionsView(LoginRequiredMixin, View):
    template_name = 'dashboard/analytics/ml_predictions.html'

    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisor_id = auth_user.get('id')
        officer_id = request.GET.get('officer_id')
        filter_type = request.GET.get('filter_type', '')
        
        # Obtener lista de oficiales
        officers_url = OFFICERS_ENDPOINTS['LIST'].format(id=supervisor_id)
        
        try:
            response = requests.get(officers_url)
            data = response.json() if response.status_code == 200 else {}
            officers = data.get('officers', [])
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching officers: {e}')
            officers = []
        
        # Obtener predicciones ML - SOLO si se seleccionó un oficial
        all_predictions = []
        if officer_id:
            predictions_url = ANALYTICS_ENDPOINTS['PREDICTIONS_BY_OFFICER'].format(id=officer_id)
        
            try:
                response = requests.get(predictions_url)
                if response.status_code == 200:
                    api_response = response.json()
                    # La API devuelve {"success": true, "data": [...]}
                    all_predictions = api_response.get('data', [])
                    
                    # Formatear datos para mejor visualización
                    for prediction in all_predictions:
                        # Formatear fecha de creación
                        if prediction.get('created_at'):
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(prediction['created_at'].replace('Z', '+00:00'))
                                prediction['created_at_formatted'] = dt.strftime('%d/%m/%Y %H:%M')
                            except:
                                prediction['created_at_formatted'] = prediction['created_at']
                        
                        # Formatear fecha de resolución si existe
                        if prediction.get('resolved_at'):
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(prediction['resolved_at'].replace('Z', '+00:00'))
                                prediction['resolved_at_formatted'] = dt.strftime('%d/%m/%Y %H:%M')
                            except:
                                prediction['resolved_at_formatted'] = prediction['resolved_at']
                                
            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching ML predictions: {e}')
                messages.error(request, 'Error al obtener predicciones ML.')
        
        # Calcular estadísticas (antes de filtrar)
        alert_count = sum(1 for p in all_predictions if p.get('requires_alert'))
        anomaly_count = sum(1 for p in all_predictions if p.get('is_anomaly'))
        
        # Aplicar filtro según el tipo seleccionado
        predictions = all_predictions
        if filter_type == 'requires_alert':
            predictions = [p for p in all_predictions if p.get('requires_alert')]
        elif filter_type == 'anomaly':
            predictions = [p for p in all_predictions if p.get('is_anomaly')]
        elif filter_type == 'high_stress':
            predictions = [p for p in all_predictions if p.get('stress_level') in ['Alto', 'Muy Alto']]
        elif filter_type == 'normal':
            predictions = [p for p in all_predictions if not p.get('requires_alert') and not p.get('is_anomaly')]
        
        context = {
            'officers': officers,
            'selected_officer_id': officer_id,
            'selected_filter': filter_type,
            'predictions': predictions,
            'total_predictions': len(all_predictions),
            'alert_count': alert_count,
            'anomaly_count': anomaly_count,
            'section': 'analytics'
        }
        
        return render(request, self.template_name, context)

# ---------------------------------------------------------------------------- #

''' CLASE: Recommendations View '''
class RecommendationsView(LoginRequiredMixin, View):
    template_name = 'dashboard/analytics/recommendations.html'

    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisor_id = auth_user.get('id')
        officer_id = request.GET.get('officer_id')
        filter_status = request.GET.get('filter_status', '')
        
        # Obtener lista de oficiales
        officers_url = OFFICERS_ENDPOINTS['LIST'].format(id=supervisor_id)
        
        try:
            response = requests.get(officers_url)
            data = response.json() if response.status_code == 200 else {}
            officers = data.get('officers', [])
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching officers: {e}')
            officers = []
        
        # Obtener recomendaciones - SOLO si se seleccionó un oficial
        all_recommendations = []
        if officer_id:
            recommendations_url = ANALYTICS_ENDPOINTS['RECOMMENDATIONS_BY_OFFICER'].format(id=officer_id)
        
            try:
                response = requests.get(recommendations_url)
                if response.status_code == 200:
                    api_response = response.json()
                    # La API devuelve {"success": true, "data": [...]}
                    all_recommendations = api_response.get('data', [])
                    
                    # Formatear datos para mejor visualización
                    for rec in all_recommendations:
                        # Formatear fecha de creación
                        if rec.get('created_at'):
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(rec['created_at'].replace('Z', '+00:00'))
                                rec['created_at_formatted'] = dt.strftime('%d/%m/%Y %H:%M')
                            except:
                                rec['created_at_formatted'] = rec['created_at']
                        
                        # Formatear fecha de resolución si existe
                        if rec.get('resolved_at'):
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(rec['resolved_at'].replace('Z', '+00:00'))
                                rec['resolved_at_formatted'] = dt.strftime('%d/%m/%Y %H:%M')
                            except:
                                rec['resolved_at_formatted'] = rec['resolved_at']
                                
            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching recommendations: {e}')
                messages.error(request, 'Error al obtener recomendaciones.')
        
        # Calcular estadísticas (antes de filtrar)
        pending_count = sum(1 for r in all_recommendations if r.get('status') == 'Pendiente')
        resolved_count = sum(1 for r in all_recommendations if r.get('status') == 'Resuelta')
        active_count = sum(1 for r in all_recommendations if r.get('is_active'))
        
        # Aplicar filtro de status
        recommendations = all_recommendations
        if filter_status == 'pending':
            recommendations = [r for r in all_recommendations if r.get('status') == 'Pendiente']
        elif filter_status == 'resolved':
            recommendations = [r for r in all_recommendations if r.get('status') == 'Resuelta']
        elif filter_status == 'active':
            recommendations = [r for r in all_recommendations if r.get('is_active')]
        
        context = {
            'officers': officers,
            'selected_officer_id': officer_id,
            'selected_filter': filter_status,
            'recommendations': recommendations,
            'total_count': len(all_recommendations),
            'pending_count': pending_count,
            'resolved_count': resolved_count,
            'active_count': active_count,
            'section': 'analytics'
        }
        
        return render(request, self.template_name, context)

# ---------------------------------------------------------------------------- #