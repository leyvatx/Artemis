"""
ML Service for Biometric Analysis

Servicio que integra el modelo de Machine Learning con el backend de Django.
Analiza datos de BPM usando VENTANAS DE TIEMPO para evitar falsos positivos.

Características:
- Analiza las últimas N lecturas en lugar de valores individuales
- Solo genera alertas cuando el patrón es SOSTENIDO
- Reduce drásticamente los falsos positivos

Este servicio NO interrumpe el flujo normal del ESP32.
"""

from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone
import logging
from statistics import mean, stdev
from datetime import timedelta

from .models import BPM
from .ml_models import MLPrediction, MLAlert

# Importar modelo de Recommendations
try:
    from apps.recommendations.models import Recommendation
    RECOMMENDATIONS_AVAILABLE = True
except ImportError:
    RECOMMENDATIONS_AVAILABLE = False

# Configuración de la ventana de tiempo
WINDOW_SIZE = 10  # Número de lecturas a analizar
MIN_READINGS_FOR_ANALYSIS = 3  # Mínimo de lecturas para hacer análisis
SUSTAINED_THRESHOLD = 3  # Lecturas consecutivas para considerar "sostenido"
TIME_WINDOW_MINUTES = 10  # Ventana de tiempo máxima en minutos

# Importar el predictor ML (lazy loading para evitar errores en importación)
_ml_predictor = None
_alert_generator = None

logger = logging.getLogger(__name__)


def get_ml_predictor():
    """
    Lazy loader para el predictor ML.
    Solo carga los modelos cuando realmente se necesitan.
    """
    global _ml_predictor
    if _ml_predictor is None:
        try:
            from ML.ml_predictor import HealthMonitorML
            _ml_predictor = HealthMonitorML()
            logger.info("ML Predictor cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando ML Predictor: {e}")
            # En desarrollo, si los modelos no existen, usar mock
            _ml_predictor = MockMLPredictor()
            logger.warning("Usando Mock ML Predictor (modelos no encontrados)")
    return _ml_predictor


def get_alert_generator():
    """
    Lazy loader para el generador de alertas.
    """
    global _alert_generator
    if _alert_generator is None:
        try:
            from ML.alert_generator import AlertGenerator
            _alert_generator = AlertGenerator()
            logger.info("Alert Generator cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando Alert Generator: {e}")
            _alert_generator = MockAlertGenerator()
            logger.warning("Usando Mock Alert Generator")
    return _alert_generator


class MockMLPredictor:
    """
    Predictor mock para desarrollo cuando los modelos ML no están disponibles.
    Analiza VENTANAS DE TIEMPO en lugar de valores individuales.
    """
    
    def predict(self, heart_rate: float, recent_hrs: Optional[list] = None, 
                user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Genera una predicción basada en la VENTANA de lecturas recientes.
        
        Args:
            heart_rate: BPM actual
            recent_hrs: Lista de BPMs recientes (los más recientes primero)
            user_id: ID del usuario
        
        Returns:
            Dict con predicción basada en análisis de ventana
        """
        
        # Construir ventana completa (actual + histórico)
        window = [heart_rate]
        if recent_hrs:
            window.extend(recent_hrs[:WINDOW_SIZE - 1])
        
        # Calcular métricas de la ventana
        window_stats = self._calculate_window_stats(window)
        
        # Determinar estrés basado en el PROMEDIO de la ventana (no valor individual)
        avg_hr = window_stats['avg']
        stress_score = min(100, max(0, (avg_hr - 60) * 2))
        
        # Ajustar stress_score por variabilidad (alta variabilidad = más estrés)
        if window_stats['variability'] > 20:
            stress_score = min(100, stress_score + 10)
        
        stress_level = self._get_stress_level(stress_score)
        
        # Determinar si hay patrón SOSTENIDO de alerta o EMERGENTE para predicción
        sustained_analysis = self._analyze_sustained_pattern(window)
        
        # Alertas: solo para patrones sostenidos
        requires_alert = sustained_analysis['requires_alert']
        # Predicciones: para patrones emergentes o sostenidos
        requires_prediction = sustained_analysis.get('requires_prediction', False)
        severity = sustained_analysis['severity']
        
        # NUEVO: También generar alerta si stress_score >= 70%
        if stress_score >= 70 and not requires_alert:
            requires_alert = True
            requires_prediction = True
            if stress_score >= 85:
                severity = 'HIGH'
            elif severity == 'LOW':
                severity = 'MEDIUM'
        
        # Detectar anomalías basadas en la ventana
        is_anomaly = self._detect_anomaly(window, window_stats)
        
        # Si es anomalía, también requiere predicción
        if is_anomaly:
            requires_prediction = True
        
        return {
            'requires_alert': requires_alert,
            'requires_prediction': requires_prediction,
            'stress_score': stress_score,
            'stress_level': stress_level,
            'severity': severity,
            'alert_probability': sustained_analysis['confidence'],
            'is_anomaly': is_anomaly,
            'hr_zone': self._get_hr_zone(avg_hr),
            'metadata': {
                'heart_rate': heart_rate,
                'window_size': len(window),
                'window_avg': round(avg_hr, 1),
                'window_max': window_stats['max'],
                'window_min': window_stats['min'],
                'variability': round(window_stats['variability'], 2),
                'trend': window_stats['trend'],
                'consecutive_high': sustained_analysis['consecutive_high'],
                'consecutive_low': sustained_analysis['consecutive_low'],
                'anomaly_score': 0.8 if is_anomaly else 0.1,
                'hr_variability': window_stats['variability'],
                'sustained_pattern': sustained_analysis['pattern_type'],
                'risk_message': sustained_analysis.get('risk_message'),
                'user_id': user_id,
                'mock_mode': True
            }
        }
    
    def _calculate_window_stats(self, window: List[float]) -> Dict[str, Any]:
        """Calcula estadísticas de la ventana de lecturas"""
        if not window:
            return {'avg': 0, 'max': 0, 'min': 0, 'variability': 0, 'trend': 'stable'}
        
        avg = mean(window)
        max_val = max(window)
        min_val = min(window)
        
        # Calcular variabilidad (desviación estándar si hay suficientes datos)
        if len(window) >= 2:
            variability = stdev(window)
        else:
            variability = 0
        
        # Calcular tendencia (comparando primera mitad con segunda mitad)
        trend = 'stable'
        if len(window) >= 4:
            mid = len(window) // 2
            first_half_avg = mean(window[mid:])  # Más antiguos
            second_half_avg = mean(window[:mid])  # Más recientes
            
            diff = second_half_avg - first_half_avg
            if diff > 10:
                trend = 'rising'
            elif diff < -10:
                trend = 'falling'
        
        return {
            'avg': avg,
            'max': max_val,
            'min': min_val,
            'variability': variability,
            'trend': trend
        }
    
    def _analyze_sustained_pattern(self, window: List[float]) -> Dict[str, Any]:
        """
        Analiza si hay un patrón SOSTENIDO que requiera alerta o patrón EMERGENTE
        que requiera predicción preventiva.
        
        Niveles:
        - CRÍTICO: 2+ lecturas críticas (>180 o <40) → Alerta inmediata
        - ALTO: 3+ lecturas altas/bajas (>140 o <50) → Alerta
        - EMERGENTE: 2 lecturas altas/bajas (>120 o <55) → Predicción preventiva
        - TENDENCIA: BPMs subiendo/bajando consistentemente → Predicción preventiva
        """
        if len(window) < MIN_READINGS_FOR_ANALYSIS:
            return {
                'requires_alert': False,
                'requires_prediction': False,
                'severity': 'LOW',
                'confidence': 0.1,
                'consecutive_high': 0,
                'consecutive_low': 0,
                'pattern_type': 'insufficient_data',
                'risk_message': None
            }
        
        # Contar lecturas consecutivas en diferentes rangos (desde la más reciente)
        consecutive_critical_high = 0
        consecutive_critical_low = 0
        consecutive_high = 0  # >140
        consecutive_low = 0   # <50
        consecutive_elevated = 0  # >120 (para predicción)
        consecutive_reduced = 0   # <55 (para predicción)
        
        # Crítico alto (>180)
        for hr in window:
            if hr > 180:
                consecutive_critical_high += 1
            else:
                break
        
        # Crítico bajo (<40)
        for hr in window:
            if hr < 40:
                consecutive_critical_low += 1
            else:
                break
        
        # Alto (>140) - para alertas
        for hr in window:
            if hr > 140:
                consecutive_high += 1
            else:
                break
        
        # Bajo (<50) - para alertas
        for hr in window:
            if hr < 50:
                consecutive_low += 1
            else:
                break
        
        # Elevado (>120) - para predicciones preventivas
        for hr in window:
            if hr > 120:
                consecutive_elevated += 1
            else:
                break
        
        # Reducido (<55) - para predicciones preventivas
        for hr in window:
            if hr < 55:
                consecutive_reduced += 1
            else:
                break
        
        # Determinar resultado
        requires_alert = False
        requires_prediction = False
        severity = 'LOW'
        confidence = 0.1
        pattern_type = 'normal'
        risk_message = None
        
        # ========== ALERTAS (Acción requerida) ==========
        
        # CRÍTICO: 2+ lecturas críticas consecutivas
        if consecutive_critical_high >= 2:
            requires_alert = True
            requires_prediction = True
            severity = 'CRITICAL'
            confidence = 0.95
            pattern_type = 'sustained_critical_high'
            risk_message = f"CRÍTICO: {consecutive_critical_high} lecturas >180 BPM consecutivas. Riesgo cardíaco severo."
        
        elif consecutive_critical_low >= 2:
            requires_alert = True
            requires_prediction = True
            severity = 'CRITICAL'
            confidence = 0.95
            pattern_type = 'sustained_critical_low'
            risk_message = f"CRÍTICO: {consecutive_critical_low} lecturas <40 BPM consecutivas. Riesgo de bradicardia severa."
        
        # ALTO: 3+ lecturas altas/bajas consecutivas
        elif consecutive_high >= SUSTAINED_THRESHOLD:
            requires_alert = True
            requires_prediction = True
            severity = 'HIGH'
            confidence = 0.85
            pattern_type = 'sustained_high'
            risk_message = f"Patrón sostenido: {consecutive_high} lecturas >140 BPM. Estrés confirmado."
        
        elif consecutive_low >= SUSTAINED_THRESHOLD:
            requires_alert = True
            requires_prediction = True
            severity = 'HIGH'
            confidence = 0.85
            pattern_type = 'sustained_low'
            risk_message = f"Patrón sostenido: {consecutive_low} lecturas <50 BPM. Bradicardia confirmada."
        
        # MEDIO-ALTO: 3+ lecturas elevadas (>120) - genera alerta de severidad MEDIUM
        elif consecutive_elevated >= SUSTAINED_THRESHOLD:
            requires_alert = True
            requires_prediction = True
            severity = 'MEDIUM'
            confidence = 0.75
            pattern_type = 'sustained_elevated'
            risk_message = f"Patrón elevado sostenido: {consecutive_elevated} lecturas >120 BPM. Riesgo de estrés."
        
        # MEDIO-BAJO: 3+ lecturas reducidas (<55) - genera alerta de severidad MEDIUM
        elif consecutive_reduced >= SUSTAINED_THRESHOLD:
            requires_alert = True
            requires_prediction = True
            severity = 'MEDIUM'
            confidence = 0.75
            pattern_type = 'sustained_reduced'
            risk_message = f"Patrón reducido sostenido: {consecutive_reduced} lecturas <55 BPM. Riesgo de bradicardia."
        
        # ========== PREDICCIONES PREVENTIVAS (Sin alerta aún) ==========
        
        # EMERGENTE ALTO: 2 lecturas elevadas (>120)
        elif consecutive_elevated >= 2:
            requires_alert = False
            requires_prediction = True
            severity = 'MEDIUM'
            confidence = 0.6
            pattern_type = 'emerging_high'
            risk_message = f"Riesgo emergente: {consecutive_elevated} lecturas >120 BPM. Si continúa, puede generar estrés."
        
        # EMERGENTE BAJO: 2 lecturas reducidas (<55)
        elif consecutive_reduced >= 2:
            requires_alert = False
            requires_prediction = True
            severity = 'MEDIUM'
            confidence = 0.6
            pattern_type = 'emerging_low'
            risk_message = f"Riesgo emergente: {consecutive_reduced} lecturas <55 BPM. Monitorear posible bradicardia."
        
        # TENDENCIA: Verificar si hay tendencia preocupante
        elif len(window) >= 4:
            trend_result = self._analyze_trend(window)
            if trend_result['is_concerning']:
                requires_alert = False
                requires_prediction = True
                severity = 'LOW'
                confidence = 0.4
                pattern_type = trend_result['trend_type']
                risk_message = trend_result['message']
        
        return {
            'requires_alert': requires_alert,
            'requires_prediction': requires_prediction,
            'severity': severity,
            'confidence': confidence,
            'consecutive_high': max(consecutive_high, consecutive_critical_high, consecutive_elevated),
            'consecutive_low': max(consecutive_low, consecutive_critical_low, consecutive_reduced),
            'pattern_type': pattern_type,
            'risk_message': risk_message
        }
    
    def _analyze_trend(self, window: List[float]) -> Dict[str, Any]:
        """
        Analiza tendencias en la ventana de BPMs.
        Detecta si los valores están subiendo o bajando consistentemente.
        """
        if len(window) < 4:
            return {'is_concerning': False, 'trend_type': 'stable', 'message': None}
        
        # Comparar mitades de la ventana
        mid = len(window) // 2
        recent_avg = mean(window[:mid])  # Más recientes
        older_avg = mean(window[mid:])   # Más antiguos
        
        diff = recent_avg - older_avg
        
        # Tendencia alcista preocupante
        if diff > 15 and recent_avg > 100:
            return {
                'is_concerning': True,
                'trend_type': 'rising_trend',
                'message': f"Tendencia alcista: BPM promedio subiendo de {older_avg:.0f} a {recent_avg:.0f}."
            }
        
        # Tendencia bajista preocupante
        elif diff < -15 and recent_avg < 60:
            return {
                'is_concerning': True,
                'trend_type': 'falling_trend',
                'message': f"Tendencia bajista: BPM promedio bajando de {older_avg:.0f} a {recent_avg:.0f}."
            }
        
        return {'is_concerning': False, 'trend_type': 'stable', 'message': None}
    
    def _detect_anomaly(self, window: List[float], stats: Dict[str, Any]) -> bool:
        """
        Detecta anomalías basadas en patrones de la ventana.
        Una anomalía es cuando hay cambios muy bruscos o patrones inusuales.
        """
        if len(window) < 3:
            return False
        
        # Alta variabilidad sostenida es anómala
        if stats['variability'] > 30:
            return True
        
        # Cambios muy bruscos entre lecturas consecutivas
        for i in range(len(window) - 1):
            if abs(window[i] - window[i + 1]) > 50:
                return True
        
        return False
    
    def _get_stress_level(self, stress_score: float) -> str:
        """Clasifica nivel de estrés"""
        if stress_score < 30:
            return 'Muy Bajo'
        elif stress_score < 50:
            return 'Bajo'
        elif stress_score < 70:
            return 'Moderado'
        elif stress_score < 85:
            return 'Alto'
        else:
            return 'Muy Alto'
    
    def _get_hr_zone(self, heart_rate: float) -> str:
        """Clasifica HR en zonas"""
        if heart_rate < 60:
            return 'Zone 1 - Recuperación'
        elif heart_rate < 100:
            return 'Zone 2 - Quema de Grasa'
        elif heart_rate < 120:
            return 'Zone 3 - Aeróbica'
        elif heart_rate < 150:
            return 'Zone 4 - Umbral Anaeróbico'
        else:
            return 'Zone 5 - Máximo Esfuerzo'


class MockAlertGenerator:
    """
    Generador de alertas mock para desarrollo.
    Solo genera alertas para patrones SOSTENIDOS.
    """
    
    def generate_alert(self, prediction_result: Dict[str, Any], 
                      user_id: int, timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Genera alerta solo si hay un patrón sostenido detectado.
        """
        
        if not prediction_result.get('requires_alert', False):
            return None
        
        metadata = prediction_result.get('metadata', {})
        hr = metadata.get('heart_rate', 0)
        window_avg = metadata.get('window_avg', hr)
        stress_score = prediction_result['stress_score']
        severity = prediction_result['severity']
        pattern_type = metadata.get('sustained_pattern', 'unknown')
        consecutive_high = metadata.get('consecutive_high', 0)
        consecutive_low = metadata.get('consecutive_low', 0)
        trend = metadata.get('trend', 'stable')
        
        # Determinar tipo de alerta basado en el PATRÓN, no en valor individual
        if pattern_type == 'sustained_critical':
            if consecutive_high > consecutive_low:
                alert_type = 'HR_CRITICAL_HIGH'
                message = (
                    f'Frecuencia cardíaca críticamente alta SOSTENIDA: '
                    f'{consecutive_high} lecturas consecutivas sobre 180 bpm. '
                    f'Promedio: {window_avg:.0f} bpm'
                )
            else:
                alert_type = 'HR_CRITICAL_LOW'
                message = (
                    f'Frecuencia cardíaca críticamente baja SOSTENIDA: '
                    f'{consecutive_low} lecturas consecutivas bajo 40 bpm. '
                    f'Promedio: {window_avg:.0f} bpm'
                )
            action_required = 'ACCIÓN INMEDIATA: Verificar estado del oficial y contactar servicios de emergencia si es necesario'
        
        elif pattern_type == 'sustained_high':
            alert_type = 'HR_SUSTAINED_ELEVATED'
            message = (
                f'Frecuencia cardíaca elevada SOSTENIDA: '
                f'{consecutive_high} lecturas consecutivas sobre 140 bpm. '
                f'Promedio de la ventana: {window_avg:.0f} bpm. '
                f'Tendencia: {self._translate_trend(trend)}'
            )
            action_required = 'Monitorear al oficial. Considerar descanso si la situación lo permite.'
        
        elif pattern_type == 'sustained_low':
            alert_type = 'HR_ABNORMALLY_LOW'
            message = (
                f'Frecuencia cardíaca baja SOSTENIDA: '
                f'{consecutive_low} lecturas consecutivas bajo 50 bpm. '
                f'Promedio de la ventana: {window_avg:.0f} bpm'
            )
            action_required = 'Verificar que el sensor esté funcionando correctamente. Si el oficial reporta malestar, actuar.'
        
        elif stress_score >= 70:
            alert_type = 'STRESS_CRITICAL'
            message = (
                f'Nivel de estrés crítico detectado: {stress_score:.1f}/100. '
                f'Basado en análisis de {metadata.get("window_size", 1)} lecturas. '
                f'Variabilidad: {metadata.get("variability", 0):.1f}'
            )
            action_required = 'El oficial muestra signos de estrés elevado sostenido. Evaluar carga de trabajo.'
        
        else:
            alert_type = 'ML_PREDICTION_ALERT'
            message = (
                f'Patrón de riesgo detectado: HR promedio {window_avg:.0f} bpm, '
                f'Estrés {stress_score:.1f}/100. Tendencia: {self._translate_trend(trend)}'
            )
            action_required = 'Mantener monitoreo del oficial'
        
        return {
            'user_id': user_id,
            'timestamp': timestamp or timezone.now().isoformat(),
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'action_required': action_required,
            'heart_rate': hr,
            'stress_score': stress_score,
            'stress_level': prediction_result['stress_level'],
            'requires_immediate_action': severity in ['CRITICAL', 'HIGH'],
            'is_anomaly': prediction_result.get('is_anomaly', False),
            'alert_probability': prediction_result['alert_probability'],
            'metadata': {
                'pattern_type': pattern_type,
                'window_avg': window_avg,
                'consecutive_readings': max(consecutive_high, consecutive_low),
                'trend': trend,
                'window_size': metadata.get('window_size', 1)
            }
        }
    
    def _translate_trend(self, trend: str) -> str:
        """Traduce tendencia a español"""
        translations = {
            'rising': 'Subiendo ⬆️',
            'falling': 'Bajando ⬇️',
            'stable': 'Estable ➡️'
        }
        return translations.get(trend, trend)


class RecommendationGenerator:
    """
    Generador de recomendaciones inteligentes basadas en patrones de ML.
    
    Genera recomendaciones automáticamente cuando se detectan:
    - Patrones de estrés sostenido
    - Alertas críticas o altas
    - Anomalías en la frecuencia cardíaca
    - Tendencias preocupantes
    """
    
    # Mapeo de patrones a recomendaciones (en español)
    RECOMMENDATION_TEMPLATES = {
        'sustained_critical_high': {
            'category': 'Salud',
            'priority': 'Crítica',
            'message': (
                'URGENTE: Se detectó frecuencia cardíaca críticamente alta sostenida ({consecutive} lecturas >180 BPM). '
                'Recomendaciones inmediatas:\n'
                '• Verificar estado físico del oficial inmediatamente\n'
                '• Considerar retiro temporal del servicio activo\n'
                '• Evaluar posibles factores de estrés extremo\n'
                '• Consultar con personal médico si persiste'
            )
        },
        'sustained_critical_low': {
            'category': 'Salud',
            'priority': 'Crítica',
            'message': (
                'URGENTE: Se detectó frecuencia cardíaca críticamente baja sostenida ({consecutive} lecturas <40 BPM). '
                'Recomendaciones inmediatas:\n'
                '• Verificar funcionamiento correcto del sensor\n'
                '• Evaluar estado de consciencia del oficial\n'
                '• Contactar servicios médicos si se confirma bradicardia\n'
                '• No permitir actividades de alto riesgo hasta evaluación médica'
            )
        },
        'sustained_high': {
            'category': 'Salud',
            'priority': 'Alta',
            'message': (
                'Patrón de frecuencia cardíaca elevada detectado ({consecutive} lecturas >140 BPM, promedio: {avg} BPM). '
                'Recomendaciones:\n'
                '• Programar descanso para el oficial cuando sea posible\n'
                '• Evaluar carga de trabajo actual\n'
                '• Monitorear hidratación y alimentación\n'
                '• Considerar rotación de tareas de alta intensidad'
            )
        },
        'sustained_low': {
            'category': 'Salud',
            'priority': 'Alta',
            'message': (
                'Patrón de frecuencia cardíaca baja detectado ({consecutive} lecturas <50 BPM). '
                'Recomendaciones:\n'
                '• Verificar que el sensor esté colocado correctamente\n'
                '• Evaluar nivel de fatiga del oficial\n'
                '• Considerar evaluación médica preventiva\n'
                '• Evitar asignaciones que requieran respuesta rápida'
            )
        },
        'sustained_elevated': {
            'category': 'Mental',
            'priority': 'Media',
            'message': (
                'Estrés moderado-alto sostenido detectado ({consecutive} lecturas >120 BPM). '
                'Recomendaciones preventivas:\n'
                '• Programar pausas breves durante el turno\n'
                '• Aplicar técnicas de respiración y relajación\n'
                '• Evaluar factores estresantes del entorno\n'
                '• Considerar apoyo de compañeros en tareas demandantes'
            )
        },
        'sustained_reduced': {
            'category': 'Salud',
            'priority': 'Media',
            'message': (
                'Frecuencia cardíaca reducida sostenida detectada ({consecutive} lecturas <55 BPM). '
                'Recomendaciones:\n'
                '• Verificar bienestar general del oficial\n'
                '• Evaluar nivel de descanso nocturno\n'
                '• Monitorear signos de fatiga extrema\n'
                '• Considerar actividad física ligera para activación'
            )
        },
        'emerging_high': {
            'category': 'Mental',
            'priority': 'Baja',
            'message': (
                'Tendencia emergente de estrés detectada ({consecutive} lecturas >120 BPM). '
                'Recomendaciones preventivas:\n'
                '• Mantener monitoreo cercano\n'
                '• Sugerir técnicas de manejo de estrés\n'
                '• Evaluar carga de trabajo próxima'
            )
        },
        'emerging_low': {
            'category': 'Salud',
            'priority': 'Baja',
            'message': (
                'Tendencia de frecuencia cardíaca baja emergente ({consecutive} lecturas <55 BPM). '
                'Recomendaciones:\n'
                '• Verificar colocación del sensor\n'
                '• Preguntar al oficial sobre su bienestar\n'
                '• Monitorear en las próximas horas'
            )
        },
        'rising_trend': {
            'category': 'Mental',
            'priority': 'Baja',
            'message': (
                'Tendencia alcista en frecuencia cardíaca detectada. '
                'Recomendaciones:\n'
                '• Observar evolución en próximas lecturas\n'
                '• Preparar opciones de descanso\n'
                '• Mantener comunicación con el oficial'
            )
        },
        'falling_trend': {
            'category': 'Salud',
            'priority': 'Baja',
            'message': (
                'Tendencia bajista en frecuencia cardíaca detectada. '
                'Recomendaciones:\n'
                '• Verificar estado de alerta del oficial\n'
                '• Evaluar signos de fatiga\n'
                '• Considerar asignación de tareas menos monótonas'
            )
        },
        'high_stress': {
            'category': 'Mental',
            'priority': 'Alta',
            'message': (
                'Nivel de estrés crítico detectado (Score: {stress_score}/100). '
                'Recomendaciones:\n'
                '• Evaluar inmediatamente la situación del oficial\n'
                '• Considerar relevación temporal\n'
                '• Proporcionar apoyo psicológico si es necesario\n'
                '• Documentar para seguimiento posterior'
            )
        },
        'anomaly_detected': {
            'category': 'Otro',
            'priority': 'Media',
            'message': (
                'Anomalía en patrones biométricos detectada (variabilidad inusual). '
                'Recomendaciones:\n'
                '• Verificar funcionamiento del equipo de monitoreo\n'
                '• Evaluar si hay factores externos afectando las lecturas\n'
                '• Documentar el incidente para análisis posterior\n'
                '• Mantener observación cercana del oficial'
            )
        }
    }
    
    def generate_recommendation(self, prediction: Dict[str, Any], 
                                 user_id: int, 
                                 alert: Optional[MLAlert] = None) -> Optional[Dict[str, Any]]:
        """
        Genera una recomendación basada en la predicción ML.
        
        Args:
            prediction: Resultado de la predicción ML
            user_id: ID del usuario
            alert: Alerta asociada (opcional)
        
        Returns:
            Dict con datos de la recomendación o None si no aplica
        """
        metadata = prediction.get('metadata', {})
        pattern_type = metadata.get('sustained_pattern', 'normal')
        stress_score = prediction.get('stress_score', 0)
        consecutive_high = metadata.get('consecutive_high', 0)
        consecutive_low = metadata.get('consecutive_low', 0)
        window_avg = metadata.get('window_avg', 0)
        
        # Determinar qué template usar
        template_key = None
        
        # Prioridad 1: Patrones específicos
        if pattern_type in self.RECOMMENDATION_TEMPLATES:
            template_key = pattern_type
        
        # Prioridad 2: Estrés alto sin patrón específico
        elif stress_score >= 70:
            template_key = 'high_stress'
        
        # Prioridad 3: Anomalía detectada
        elif prediction.get('is_anomaly', False):
            template_key = 'anomaly_detected'
        
        # Si no hay template aplicable, no generar recomendación
        if not template_key:
            return None
        
        template = self.RECOMMENDATION_TEMPLATES[template_key]
        consecutive = max(consecutive_high, consecutive_low)
        
        # Formatear mensaje con datos reales
        message = template['message'].format(
            consecutive=consecutive,
            avg=f"{window_avg:.0f}",
            stress_score=f"{stress_score:.1f}"
        )
        
        return {
            'user_id': user_id,
            'category': template['category'],
            'priority': template['priority'],
            'message': message,
            'alert_id': alert.id if alert else None,
            'pattern_type': pattern_type,
            'stress_score': stress_score
        }


# Instancia global del generador de recomendaciones
_recommendation_generator = None

def get_recommendation_generator():
    """Lazy loader para el generador de recomendaciones"""
    global _recommendation_generator
    if _recommendation_generator is None:
        _recommendation_generator = RecommendationGenerator()
    return _recommendation_generator


class MLAnalysisService:
    """
    Servicio principal para análisis ML de datos biométricos.
    
    Este servicio:
    1. Recibe datos de BPM guardados en la BD
    2. Obtiene histórico del usuario
    3. Ejecuta predicción ML
    4. Guarda predicción en MLPrediction
    5. Si requiere alerta, crea MLAlert
    6. Genera recomendaciones inteligentes automáticamente
    7. Todo esto SIN interrumpir el flujo del ESP32
    """
    
    def __init__(self):
        self.predictor = get_ml_predictor()
        self.alert_generator = get_alert_generator()
        self.recommendation_generator = get_recommendation_generator()
    
    def analyze_bpm(self, bpm_instance: BPM) -> Dict[str, Any]:
        """
        Analiza un registro de BPM y genera predicción ML.
        
        OPTIMIZACIÓN: Solo guarda predicciones cuando hay algo RELEVANTE:
        - Estrés alto (>= 70)
        - Es una anomalía
        - Hay patrón emergente o sostenido
        - Requiere alerta
        
        BPMs normales se procesan pero NO se guardan para evitar saturar la BD.
        
        Args:
            bpm_instance: Instancia de BPM ya guardada en la BD
        
        Returns:
            Dict con información del análisis realizado
        """
        try:
            # 1. Obtener histórico reciente del usuario (últimos 10 registros)
            recent_bpms = BPM.objects.filter(
                user=bpm_instance.user
            ).exclude(
                id=bpm_instance.id  # Excluir el actual
            ).order_by('-created_at')[:10].values_list('value', flat=True)
            
            recent_hrs = list(recent_bpms) if recent_bpms else None
            
            # 2. Ejecutar predicción ML
            prediction = self.predictor.predict(
                heart_rate=float(bpm_instance.value),
                recent_hrs=recent_hrs,
                user_id=bpm_instance.user_id
            )
            
            # 3. Determinar si es RELEVANTE para guardar
            is_relevant = self._is_prediction_relevant(prediction)
            
            ml_prediction = None
            alert_created = None
            recommendation_created = None
            
            if is_relevant:
                # Solo guardar predicción si es relevante
                ml_prediction = self._save_prediction(bpm_instance, prediction)
                logger.info(f"Predicción ML guardada: {ml_prediction.id} para BPM {bpm_instance.id} (relevante)")
                
                # 4. Si requiere alerta, generarla
                if prediction['requires_alert']:
                    alert_created = self._generate_and_save_alert(
                        ml_prediction, 
                        prediction, 
                        bpm_instance
                    )
                
                # 5. Generar recomendación inteligente
                recommendation_created = self._generate_and_save_recommendation(
                    prediction,
                    bpm_instance,
                    alert_created
                )
            else:
                # BPM normal - verificar si hay alertas activas para auto-resolver
                self._auto_resolve_if_stabilized(bpm_instance, prediction)
                logger.debug(f"BPM {bpm_instance.id} procesado - valores normales, no se guarda predicción")
            
            return {
                'success': True,
                'prediction_id': ml_prediction.id if ml_prediction else None,
                'prediction_saved': is_relevant,
                'requires_alert': prediction['requires_alert'],
                'alert_created': alert_created is not None,
                'alert_id': alert_created.id if alert_created else None,
                'recommendation_created': recommendation_created is not None,
                'recommendation_id': recommendation_created.recommendation_id if recommendation_created else None,
                'stress_score': prediction['stress_score'],
                'severity': prediction['severity'],
                'pattern_type': prediction['metadata'].get('sustained_pattern', 'normal')
            }
            
        except Exception as e:
            logger.error(f"Error en análisis ML para BPM {bpm_instance.id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'bpm_id': bpm_instance.id
            }
    
    def _is_prediction_relevant(self, prediction: Dict[str, Any]) -> bool:
        """
        Determina si una predicción es relevante para guardar en la BD.
        
        SIMPLIFICADO: Usa el campo 'requires_prediction' del análisis de patrones.
        
        Se guarda predicción cuando:
        - El análisis de patrones indica que es relevante (requires_prediction=True)
        - Es una anomalía
        - Requiere alerta
        
        NO se guarda cuando:
        - BPMs normales sin patrones emergentes
        
        Returns:
            True si debe guardarse, False si es un BPM normal
        """
        # Usar el nuevo campo requires_prediction del análisis
        if prediction.get('requires_prediction', False):
            return True
        
        # Siempre guardar si requiere alerta
        if prediction.get('requires_alert', False):
            return True
        
        # Guardar si es anomalía
        if prediction.get('is_anomaly', False):
            return True
        
        # No es relevante, no guardar
        return False
    
    @transaction.atomic
    def _save_prediction(self, bpm_instance: BPM, prediction: Dict[str, Any]) -> MLPrediction:
        """
        Guarda la predicción ML en la base de datos.
        Solo crea UNA predicción por patrón sostenido, actualizando la existente si hay una reciente.
        """
        # Verificar si ya existe una predicción activa reciente para este usuario
        # para evitar crear múltiples predicciones por el mismo patrón sostenido
        recent_prediction = MLPrediction.objects.filter(
            user=bpm_instance.user,
            requires_alert=True,  # Solo agrupar predicciones que requieren alerta
            created_at__gte=timezone.now() - timedelta(minutes=TIME_WINDOW_MINUTES)
        ).order_by('-created_at').first()
        
        if recent_prediction:
            # Ya hay una predicción activa reciente, actualizar en lugar de crear nueva
            logger.info(
                f"Actualizando predicción existente {recent_prediction.id} para usuario {bpm_instance.user_id}. "
                f"No se creará duplicado."
            )
            # Actualizar la predicción existente con los nuevos datos
            metadata = recent_prediction.metadata or {}
            metadata['last_bpm'] = float(bpm_instance.value)
            metadata['last_update'] = timezone.now().isoformat()
            metadata['bpm_count'] = metadata.get('bpm_count', 1) + 1
            metadata['window_avg'] = prediction['metadata'].get('window_avg', metadata.get('window_avg'))
            
            recent_prediction.metadata = metadata
            recent_prediction.stress_score = prediction['stress_score']
            recent_prediction.stress_level = prediction['stress_level']
            recent_prediction.severity = prediction['severity']
            recent_prediction.hr_variability = prediction['metadata'].get('hr_variability')
            recent_prediction.save()
            
            return recent_prediction
        
        # No hay predicción reciente, crear una nueva
        ml_prediction = MLPrediction.objects.create(
            bpm=bpm_instance,
            user=bpm_instance.user,
            stress_score=prediction['stress_score'],
            stress_level=prediction['stress_level'],
            requires_alert=prediction['requires_alert'],
            alert_probability=prediction['alert_probability'],
            severity=prediction['severity'],
            is_anomaly=prediction['is_anomaly'],
            anomaly_score=prediction['metadata'].get('anomaly_score'),
            hr_zone=prediction['hr_zone'],
            hr_variability=prediction['metadata'].get('hr_variability'),
            metadata=prediction['metadata']
        )
        
        return ml_prediction
    
    @transaction.atomic
    def _generate_and_save_alert(self, ml_prediction: MLPrediction, 
                                 prediction: Dict[str, Any], 
                                 bpm_instance: BPM) -> Optional[MLAlert]:
        """
        Genera y guarda una alerta ML si es necesario.
        Solo crea UNA alerta por patrón sostenido, no una por cada BPM.
        
        Una nueva alerta se puede crear si:
        - No hay alertas activas recientes, O
        - La alerta anterior tiene pattern_ended=True (BPMs se estabilizaron)
        """
        try:
            logger.info(f"Intentando generar alerta para predicción {ml_prediction.id}, requires_alert={prediction.get('requires_alert')}")
            
            # Verificar si ya existe una alerta activa reciente para este usuario
            # que NO tenga el patrón terminado
            recent_alert = MLAlert.objects.filter(
                user=bpm_instance.user,
                status__in=['Pending', 'Acknowledged'],  # Alertas no resueltas
                created_at__gte=timezone.now() - timedelta(minutes=TIME_WINDOW_MINUTES)
            ).order_by('-created_at').first()
            
            if recent_alert:
                metadata = recent_alert.metadata or {}
                
                # Si el patrón anterior ya terminó, permitir crear nueva alerta
                if metadata.get('pattern_ended', False):
                    logger.info(
                        f"Alerta {recent_alert.id} tiene patrón terminado. "
                        f"Se creará nueva alerta para nuevo evento."
                    )
                    # Continuar para crear nueva alerta
                else:
                    # Patrón aún activo, actualizar la alerta existente
                    logger.info(
                        f"Ya existe alerta activa {recent_alert.id} para usuario {bpm_instance.user_id}. "
                        f"Actualizando con nuevo BPM. No se creará duplicado."
                    )
                    metadata['last_bpm'] = float(bpm_instance.value)
                    metadata['last_update'] = timezone.now().isoformat()
                    metadata['bpm_count'] = metadata.get('bpm_count', 1) + 1
                    recent_alert.metadata = metadata
                    recent_alert.heart_rate = float(bpm_instance.value)
                    recent_alert.stress_score = prediction.get('stress_score', recent_alert.stress_score)
                    recent_alert.save()
                    return None
            
            # Generar payload de alerta
            alert_payload = self.alert_generator.generate_alert(
                prediction_result=prediction,
                user_id=bpm_instance.user_id,
                timestamp=bpm_instance.created_at.isoformat()
            )
            
            if not alert_payload:
                logger.info(f"No se generó payload de alerta para predicción {ml_prediction.id}")
                return None
            
            logger.info(f"Payload de alerta generado: {alert_payload.get('alert_type')}, {alert_payload.get('severity')}")
            
            # Crear alerta en la BD
            ml_alert = MLAlert.objects.create(
                user=bpm_instance.user,
                prediction=ml_prediction,
                alert_type=alert_payload['alert_type'],
                severity=alert_payload['severity'],
                message=alert_payload['message'],
                action_required=alert_payload['action_required'],
                heart_rate=alert_payload['heart_rate'],
                stress_score=alert_payload['stress_score'],
                stress_level=alert_payload['stress_level'],
                requires_immediate_action=alert_payload['requires_immediate_action'],
                is_anomaly=alert_payload['is_anomaly'],
                metadata=alert_payload['metadata']
            )
            
            logger.warning(
                f"ALERTA ML CREADA: {ml_alert.alert_type} ({ml_alert.severity}) "
                f"para usuario {bpm_instance.user_id}"
            )
            
            # Si es crítica o alta, se podría notificar supervisores aquí
            if ml_alert.requires_immediate_action:
                self._notify_supervisors(ml_alert)
            
            return ml_alert
            
        except Exception as e:
            logger.error(f"Error generando alerta ML: {e}", exc_info=True)
            return None
    
    def _notify_supervisors(self, ml_alert: MLAlert):
        """
        Notifica a los supervisores sobre alertas críticas.
        
        TODO: Implementar notificaciones (email, push, etc.)
        Por ahora solo loguea la necesidad de notificar.
        """
        logger.critical(
            f"NOTIFICACIÓN REQUERIDA: Alerta {ml_alert.id} ({ml_alert.severity}) "
            f"para usuario {ml_alert.user_id} - {ml_alert.message}"
        )
        
        # Aquí se podría:
        # - Enviar email a supervisores
        # - Enviar notificación push
        # - Crear registro en sistema de eventos
        # - etc.
    
    def _auto_resolve_if_stabilized(self, bpm_instance: BPM, prediction: Dict[str, Any]):
        """
        Marca el patrón de una alerta como "terminado" cuando los BPMs se estabilizan.
        
        NO resuelve la alerta (eso lo hace el supervisor manualmente),
        pero permite que se creen nuevas alertas si hay otro evento de estrés.
        
        Criterio de estabilización:
        - BPM actual < 100 (zona normal)
        - Stress score < 50
        """
        try:
            current_hr = float(bpm_instance.value)
            stress_score = prediction.get('stress_score', 0)
            
            # Verificar si los valores son normales/estables
            is_stabilized = current_hr < 100 and stress_score < 50
            
            if not is_stabilized:
                return  # Aún no estabilizado
            
            # Buscar alertas activas recientes que NO tengan pattern_ended
            active_alerts = MLAlert.objects.filter(
                user=bpm_instance.user,
                status__in=['Pending', 'Acknowledged'],
                created_at__gte=timezone.now() - timedelta(minutes=TIME_WINDOW_MINUTES)
            )
            
            for alert in active_alerts:
                metadata = alert.metadata or {}
                if not metadata.get('pattern_ended', False):
                    # Marcar el patrón como terminado
                    metadata['pattern_ended'] = True
                    metadata['stabilized_at'] = timezone.now().isoformat()
                    metadata['stabilized_hr'] = current_hr
                    metadata['stabilized_stress'] = stress_score
                    alert.metadata = metadata
                    alert.save()
                    
                    logger.info(
                        f"Patrón terminado para alerta {alert.id}. "
                        f"BPMs estabilizados (HR={current_hr}, Stress={stress_score}). "
                        f"Nuevas alertas permitidas."
                    )
                    
        except Exception as e:
            logger.error(f"Error en auto_resolve_if_stabilized: {e}", exc_info=True)
    
    @transaction.atomic
    def _generate_and_save_recommendation(self, prediction: Dict[str, Any],
                                          bpm_instance: BPM,
                                          alert: Optional[MLAlert] = None) -> Optional[Any]:
        """
        Genera y guarda una recomendación inteligente basada en la predicción ML.
        
        Solo crea UNA recomendación por patrón, evitando duplicados.
        """
        if not RECOMMENDATIONS_AVAILABLE:
            logger.debug("Modelo Recommendation no disponible, saltando generación")
            return None
        
        try:
            # Generar payload de recomendación
            rec_payload = self.recommendation_generator.generate_recommendation(
                prediction=prediction,
                user_id=bpm_instance.user_id,
                alert=alert
            )
            
            if not rec_payload:
                logger.debug(f"No se generó recomendación para BPM {bpm_instance.id} - patrón normal")
                return None
            
            # Verificar si ya existe una recomendación activa reciente para este usuario
            # con el mismo tipo de patrón para evitar duplicados
            pattern_type = rec_payload.get('pattern_type', 'unknown')
            recent_rec = Recommendation.objects.filter(
                user=bpm_instance.user,
                status='Pendiente',
                created_at__gte=timezone.now() - timedelta(minutes=TIME_WINDOW_MINUTES * 2)
            ).order_by('-created_at').first()
            
            if recent_rec:
                logger.info(
                    f"Ya existe recomendación activa {recent_rec.recommendation_id} para usuario {bpm_instance.user_id}. "
                    f"No se creará duplicado."
                )
                return None
            
            # Crear recomendación en la BD
            from apps.alerts.models import Alert
            
            recommendation = Recommendation.objects.create(
                user=bpm_instance.user,
                alert=Alert.objects.filter(user=bpm_instance.user).last() if not alert else None,
                message=rec_payload['message'],
                category=rec_payload['category'],
                priority=rec_payload['priority'],
                status='Pendiente',
                is_active=True
            )
            
            logger.info(
                f"RECOMENDACIÓN CREADA: [{recommendation.priority}] {recommendation.category} "
                f"para usuario {bpm_instance.user_id} - Patrón: {pattern_type}"
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generando recomendación: {e}", exc_info=True)
            return None
    
    def get_user_risk_summary(self, user_id: int, hours: int = 24) -> Dict[str, Any]:
        """
        Obtiene un resumen del riesgo de un usuario en las últimas N horas.
        
        Útil para dashboards de supervisores.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        predictions = MLPrediction.objects.filter(
            user_id=user_id,
            created_at__gte=cutoff_time
        )
        
        alerts = MLAlert.objects.filter(
            user_id=user_id,
            created_at__gte=cutoff_time,
            status='Pending'
        )
        
        total_predictions = predictions.count()
        
        if total_predictions == 0:
            return {
                'user_id': user_id,
                'period_hours': hours,
                'no_data': True
            }
        
        # Calcular estadísticas
        avg_stress = predictions.aggregate(
            avg=models.Avg('stress_score')
        )['avg'] or 0
        
        high_stress_count = predictions.filter(
            stress_level__in=['Alto', 'Muy Alto']
        ).count()
        
        anomaly_count = predictions.filter(is_anomaly=True).count()
        
        critical_alerts = alerts.filter(severity='CRITICAL').count()
        high_alerts = alerts.filter(severity='HIGH').count()
        
        return {
            'user_id': user_id,
            'period_hours': hours,
            'total_readings': total_predictions,
            'avg_stress_score': round(avg_stress, 1),
            'high_stress_periods': high_stress_count,
            'anomalies_detected': anomaly_count,
            'pending_alerts': alerts.count(),
            'critical_alerts': critical_alerts,
            'high_alerts': high_alerts,
            'risk_level': self._calculate_risk_level(avg_stress, critical_alerts, high_alerts)
        }
    
    def _calculate_risk_level(self, avg_stress: float, critical: int, high: int) -> str:
        """Calcula nivel de riesgo general"""
        if critical > 0 or avg_stress > 85:
            return 'CRITICAL'
        elif high > 0 or avg_stress > 70:
            return 'HIGH'
        elif avg_stress > 50:
            return 'MEDIUM'
        else:
            return 'LOW'


# Singleton global del servicio ML
_ml_service_instance = None

def get_ml_service() -> MLAnalysisService:
    """
    Retorna la instancia singleton del servicio ML.
    """
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLAnalysisService()
    return _ml_service_instance


# Importar models para las queries
from django.db import models
