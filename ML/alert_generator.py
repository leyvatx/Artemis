"""
Alert Generator Module for Artemis Health Monitoring System
=============================================================

Este módulo genera alertas automáticas basadas en predicciones ML.
Cumple con SRS FR-006: Automatic Alert Activation

Responsabilidades:
- Clasificar tipo de alerta según predicción ML
- Determinar severidad (CRITICAL/HIGH/MEDIUM/LOW)
- Generar payload estructurado para el backend
- Crear mensajes descriptivos para supervisores

El backend usa este módulo para decidir cuándo y cómo alertar.
"""

from datetime import datetime
from typing import Dict, Any, Optional


class AlertGenerator:
    """
    Generador de alertas automáticas basado en predicciones ML.
    
    Analiza resultados de ml_predictor y genera payloads de alerta
    listos para ser guardados en la base de datos por el backend.
    """
    
    def __init__(self):
        """Inicializa el generador con umbrales configurados"""
        self.thresholds = {
            # Umbrales de frecuencia cardíaca (SRS FR-006)
            'hr_critical_low': 40,      # < 40 bpm = emergencia
            'hr_critical_high': 180,    # > 180 bpm = emergencia
            'hr_warning_low': 50,       # < 50 bpm = advertencia
            'hr_warning_high': 150,     # > 150 bpm = advertencia
            
            # Umbrales de estrés
            'stress_critical': 85,      # >= 85 = estrés crítico
            'stress_high': 70,          # >= 70 = estrés alto
            'stress_medium': 50,        # >= 50 = estrés moderado
            
            # Otros umbrales
            'anomaly_threshold': 0.8,   # Probabilidad de alerta > 80%
        }
        
        print("AlertGenerator inicializado con umbrales configurados")
    
    def generate_alert(self, 
                      prediction_result: Dict[str, Any], 
                      user_id: int,
                      timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Genera un payload de alerta si es necesario.
        
        Args:
            prediction_result: Resultado de ml_predictor.predict()
            user_id: ID del oficial/usuario
            timestamp: Timestamp del evento (opcional, usa now() si None)
        
        Returns:
            Dict con payload de alerta o None si no requiere alerta
            
        Example:
            >>> alert_gen = AlertGenerator()
            >>> prediction = predictor.predict(heart_rate=185)
            >>> alert = alert_gen.generate_alert(prediction, user_id=123)
            >>> if alert:
            ...     # Backend guarda alert en DB
            ...     Alert.objects.create(**alert)
        """
        # Si el modelo ML dice que no requiere alerta, retornar None
        if not prediction_result.get('requires_alert', False):
            return None
        
        # Extraer datos de la predicción
        hr = prediction_result['metadata']['heart_rate']
        stress_score = prediction_result['stress_score']
        stress_level = prediction_result['stress_level']
        is_anomaly = prediction_result['is_anomaly']
        alert_probability = prediction_result['alert_probability']
        
        # Clasificar tipo y severidad de alerta
        alert_type, severity, message, action_required = self._classify_alert(
            hr=hr,
            stress_score=stress_score,
            stress_level=stress_level,
            is_anomaly=is_anomaly,
            alert_probability=alert_probability,
            metadata=prediction_result['metadata']
        )
        
        # Si no se pudo clasificar, retornar None
        if alert_type is None:
            return None
        
        # Construir payload de alerta
        alert_payload = {
            # Identificación
            'user_id': user_id,
            'timestamp': timestamp or datetime.now().isoformat(),
            
            # Clasificación
            'alert_type': alert_type,
            'severity': severity,
            
            # Mensaje
            'message': message,
            'action_required': action_required,
            
            # Datos biométricos
            'heart_rate': float(hr),
            'stress_score': float(stress_score),
            'stress_level': stress_level,
            
            # Flags
            'requires_immediate_action': severity in ['CRITICAL', 'HIGH'],
            'is_anomaly': bool(is_anomaly),
            'alert_probability': float(alert_probability),
            
            # Metadatos ML
            'metadata': {
                'hr_zone': prediction_result['hr_zone'],
                'hr_variability': prediction_result['metadata'].get('hr_variability', 0),
                'hr_elevated_sustained': prediction_result['metadata'].get('hr_elevated_sustained', 0),
                'hr_rapid_changes': prediction_result['metadata'].get('hr_rapid_changes', 0),
                'anomaly_score': prediction_result['metadata'].get('anomaly_score', 0),
                'ml_features': prediction_result['metadata']['features']
            }
        }
        
        return alert_payload
    
    def _classify_alert(self, 
                       hr: float, 
                       stress_score: float,
                       stress_level: str,
                       is_anomaly: bool,
                       alert_probability: float,
                       metadata: Dict) -> tuple:
        """
        Clasifica el tipo y severidad de la alerta.
        
        Returns:
            tuple: (alert_type, severity, message, action_required)
        """
        
        # ===== CASOS CRÍTICOS (EMERGENCIA MÉDICA) =====
        
        # CASO 1: HR críticamente baja (bradicardia severa)
        if hr < self.thresholds['hr_critical_low']:
            return (
                'HR_CRITICAL_LOW',
                'CRITICAL',
                f'EMERGENCIA: Frecuencia cardíaca críticamente baja ({hr:.0f} bpm). '
                f'Posible bradicardia severa. Requiere atención médica inmediata.',
                'Contactar al oficial de inmediato. Evaluar estado de consciencia. '
                'Preparar asistencia médica de emergencia.'
            )
        
        # CASO 2: HR críticamente alta (taquicardia severa)
        if hr > self.thresholds['hr_critical_high']:
            return (
                'HR_CRITICAL_HIGH',
                'CRITICAL',
                f'EMERGENCIA: Frecuencia cardíaca críticamente alta ({hr:.0f} bpm). '
                f'Posible taquicardia severa o crisis cardiovascular.',
                'Contactar al oficial de inmediato. Verificar si está en emergencia. '
                'Alertar servicios médicos si es necesario.'
            )
        
        # CASO 3: HR = 0 (sensor desconectado o problema crítico)
        if hr == 0:
            return (
                'HR_ZERO',
                'CRITICAL',
                'ALERTA CRÍTICA: Sin señal de frecuencia cardíaca (0 bpm). '
                'Dispositivo desconectado o situación de emergencia.',
                'Contactar al oficial INMEDIATAMENTE. Verificar estado del dispositivo. '
                'Confirmar bienestar del oficial.'
            )
        
        # ===== CASOS DE ALTO RIESGO =====
        
        # CASO 4: Estrés crítico (muy alto)
        if stress_score >= self.thresholds['stress_critical']:
            return (
                'STRESS_CRITICAL',
                'HIGH',
                f'ESTRÉS CRÍTICO: Nivel de estrés muy alto detectado ({stress_score:.1f}/100). '
                f'El oficial está bajo estrés severo que puede afectar su desempeño y salud.',
                'Monitorear de cerca al oficial. Considerar rotación de tareas o descanso. '
                'Evaluar factores estresantes en el entorno.'
            )
        
        # CASO 5: Alto riesgo de estrés
        if stress_score >= self.thresholds['stress_high']:
            return (
                'STRESS_HIGH_RISK',
                'HIGH',
                f'ALTO RIESGO DE ESTRÉS: Score de estrés elevado ({stress_score:.1f}/100). '
                f'Nivel: {stress_level}. Requiere atención preventiva.',
                'Verificar estado del oficial. Considerar intervención preventiva. '
                'Revisar carga de trabajo actual.'
            )
        
        # CASO 6: HR anormalmente alta (pero no crítica)
        if hr > self.thresholds['hr_warning_high']:
            return (
                'HR_ABNORMALLY_HIGH',
                'HIGH',
                f'FRECUENCIA CARDÍACA ANORMALMENTE ALTA: {hr:.0f} bpm. '
                f'Por encima del umbral de advertencia ({self.thresholds["hr_warning_high"]} bpm).',
                'Verificar si el oficial está en actividad física intensa. '
                'Si está en reposo, evaluar posible estrés o problema de salud.'
            )
        
        # CASO 7: HR anormalmente baja (pero no crítica)
        if hr < self.thresholds['hr_warning_low']:
            return (
                'HR_ABNORMALLY_LOW',
                'HIGH',
                f'FRECUENCIA CARDÍACA ANORMALMENTE BAJA: {hr:.0f} bpm. '
                f'Por debajo del umbral de advertencia ({self.thresholds["hr_warning_low"]} bpm).',
                'Verificar estado del oficial. Confirmar que el sensor funciona correctamente. '
                'Evaluar si hay síntomas asociados (mareo, fatiga).'
            )
        
        # ===== CASOS MODERADOS =====
        
        # CASO 8: Estrés moderado-alto
        if stress_score >= self.thresholds['stress_medium']:
            return (
                'STRESS_ELEVATED',
                'MEDIUM',
                f'ESTRÉS ELEVADO: Nivel de estrés moderado-alto ({stress_score:.1f}/100). '
                f'Nivel: {stress_level}.',
                'Monitorear evolución del estrés. Si persiste, considerar medidas preventivas. '
                'Mantener comunicación con el oficial.'
            )
        
        # CASO 9: HR elevada sostenida
        if metadata.get('hr_elevated_sustained', 0) == 1:
            return (
                'HR_SUSTAINED_ELEVATED',
                'MEDIUM',
                f'FRECUENCIA CARDÍACA ELEVADA SOSTENIDA: {hr:.0f} bpm mantenida por período prolongado. '
                f'Puede indicar estrés continuo.',
                'Verificar duración del episodio. Evaluar si es por actividad física o estrés. '
                'Considerar descanso si es prolongado.'
            )
        
        # CASO 10: Cambios rápidos en HR (estrés agudo)
        rapid_changes = metadata.get('hr_rapid_changes', 0)
        if rapid_changes >= 3:
            return (
                'HR_RAPID_FLUCTUATION',
                'MEDIUM',
                f'FLUCTUACIONES RÁPIDAS EN HR: {rapid_changes} cambios bruscos detectados. '
                f'Puede indicar estrés agudo o situación de alta demanda.',
                'Observar contexto del oficial. Verificar si está en situación de alto estrés. '
                'Confirmar estabilidad emocional.'
            )
        
        # CASO 11: Anomalía detectada por ML
        if is_anomaly and alert_probability > self.thresholds['anomaly_threshold']:
            return (
                'ANOMALY_DETECTED',
                'MEDIUM',
                f'ANOMALÍA DETECTADA: Patrón cardíaco inusual identificado por ML. '
                f'Probabilidad de alerta: {alert_probability:.1%}.',
                'Revisar patrón de HR del oficial. Comparar con su historial normal. '
                'Verificar bienestar general.'
            )
        
        # CASO 12: Alerta general por modelo ML
        if alert_probability > 0.7:
            return (
                'ML_PREDICTION_ALERT',
                'MEDIUM',
                f'ALERTA PREDICTIVA: El modelo ML ha detectado un patrón que requiere atención. '
                f'Probabilidad: {alert_probability:.1%}. HR: {hr:.0f} bpm, Estrés: {stress_score:.1f}/100.',
                'Revisar contexto completo del oficial. Evaluar métricas adicionales. '
                'Mantener observación.'
            )
        
        # Si llegamos aquí, no hay clasificación específica
        return None, None, None, None
    
    def get_alert_summary(self, alerts: list) -> Dict[str, Any]:
        """
        Genera un resumen de múltiples alertas.
        Útil para reportes o dashboard de supervisores.
        
        Args:
            alerts: Lista de alertas generadas
        
        Returns:
            Dict con resumen estadístico
        """
        if not alerts:
            return {
                'total_alerts': 0,
                'by_severity': {},
                'by_type': {},
                'critical_count': 0,
                'requires_immediate_action': 0
            }
        
        # Contadores
        by_severity = {}
        by_type = {}
        critical_count = 0
        immediate_action_count = 0
        
        for alert in alerts:
            # Contar por severidad
            severity = alert.get('severity', 'UNKNOWN')
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Contar por tipo
            alert_type = alert.get('alert_type', 'UNKNOWN')
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            
            # Contar críticos
            if severity == 'CRITICAL':
                critical_count += 1
            
            # Contar que requieren acción inmediata
            if alert.get('requires_immediate_action', False):
                immediate_action_count += 1
        
        return {
            'total_alerts': len(alerts),
            'by_severity': by_severity,
            'by_type': by_type,
            'critical_count': critical_count,
            'requires_immediate_action': immediate_action_count,
            'severity_distribution': {
                'critical_pct': (by_severity.get('CRITICAL', 0) / len(alerts) * 100),
                'high_pct': (by_severity.get('HIGH', 0) / len(alerts) * 100),
                'medium_pct': (by_severity.get('MEDIUM', 0) / len(alerts) * 100),
                'low_pct': (by_severity.get('LOW', 0) / len(alerts) * 100)
            }
        }
    
    def update_thresholds(self, new_thresholds: Dict[str, float]):
        """
        Actualiza los umbrales del generador de alertas.
        Útil para ajustar sensibilidad del sistema.
        
        Args:
            new_thresholds: Dict con nuevos valores de umbrales
        """
        self.thresholds.update(new_thresholds)
        print(f"Umbrales actualizados: {new_thresholds}")


# Ejemplo de uso y testing
if __name__ == "__main__":
    import json
    from ml_predictor import HealthMonitorML
    
    print("=" * 70)
    print("ARTEMIS ALERT GENERATOR - TEST DE FUNCIONALIDAD")
    print("=" * 70)
    
    # Inicializar predictor y generador
    predictor = HealthMonitorML()
    alert_gen = AlertGenerator()
    
    # Casos de prueba
    test_cases = [
        {
            'hr': 75,
            'user_id': 1,
            'desc': 'Normal en reposo',
            'recent': [72, 73, 74, 75, 76, 74, 73, 75, 76, 75]
        },
        {
            'hr': 35,
            'user_id': 2,
            'desc': 'CRÍTICO - HR muy baja',
            'recent': [38, 37, 36, 35, 34, 35, 36, 35, 35, 35]
        },
        {
            'hr': 195,
            'user_id': 3,
            'desc': 'CRÍTICO - HR muy alta',
            'recent': [150, 160, 170, 180, 185, 188, 190, 192, 194, 195]
        },
        {
            'hr': 140,
            'user_id': 4,
            'desc': 'ALTO - Estrés elevado',
            'recent': [120, 125, 128, 132, 135, 137, 138, 139, 140, 140]
        },
        {
            'hr': 105,
            'user_id': 5,
            'desc': 'MEDIO - HR elevada sostenida',
            'recent': [102, 103, 104, 105, 104, 105, 106, 105, 104, 105]
        }
    ]
    
    print("\n" + "=" * 70)
    print("CASOS DE PRUEBA")
    print("=" * 70)
    
    all_alerts = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Caso {i}: {test['desc']}")
        print(f"   Usuario: {test['user_id']} | HR: {test['hr']} bpm")
        print(f"{'─' * 70}")
        
        # Predicción ML
        prediction = predictor.predict(
            heart_rate=test['hr'],
            recent_hrs=test['recent'],
            user_id=test['user_id']
        )
        
        print(f"\nPREDICCIÓN ML:")
        print(f"   • Requiere alerta: {'SÍ' if prediction['requires_alert'] else 'NO'}")
        print(f"   • Probabilidad: {prediction['alert_probability']:.1%}")
        print(f"   • Estrés: {prediction['stress_score']:.1f}/100 ({prediction['stress_level']})")
        print(f"   • Severidad ML: {prediction['severity']}")
        
        # Generar alerta
        alert = alert_gen.generate_alert(prediction, test['user_id'])
        
        if alert:
            all_alerts.append(alert)
            print(f"\nALERTA GENERADA:")
            print(f"   • Tipo: {alert['alert_type']}")
            print(f"   • Severidad: {alert['severity']}")
            print(f"   • Acción inmediata: {'SÍ' if alert['requires_immediate_action'] else 'NO'}")
            print(f"   • Mensaje:")
            print(f"     {alert['message']}")
            print(f"   • Acción requerida:")
            print(f"     {alert['action_required']}")
        else:
            print(f"\nSIN ALERTA")
            print(f"   Estado normal. No requiere acción.")
    
    # Resumen de alertas
    print("\n" + "=" * 70)
    print("RESUMEN DE ALERTAS GENERADAS")
    print("=" * 70)
    
    summary = alert_gen.get_alert_summary(all_alerts)
    
    print(f"\nEstadísticas:")
    print(f"   • Total de alertas: {summary['total_alerts']}")
    print(f"   • Alertas críticas: {summary['critical_count']}")
    print(f"   • Requieren acción inmediata: {summary['requires_immediate_action']}")
    
    print(f"\nPor severidad:")
    for severity, count in summary['by_severity'].items():
        pct = summary['severity_distribution'][f'{severity.lower()}_pct']
        print(f"   • {severity}: {count} ({pct:.1f}%)")
    
    print(f"\nPor tipo:")
    for alert_type, count in summary['by_type'].items():
        print(f"   • {alert_type}: {count}")
    
    print("\nTest completado exitosamente")
    print("=" * 70)
