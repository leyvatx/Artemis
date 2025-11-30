"""
ML Health Monitoring Service for Artemis
=========================================

Servicio unificado que integra predicción ML y generación de alertas.
Este es el módulo principal que el backend Django debe consumir.

Responsabilidades:
- Integrar ml_predictor + alert_generator
- Proveer interfaz simple para el backend
- Manejar análisis individual y por lotes
- Singleton pattern para eficiencia

Uso desde Django:
    from ML.ml_service import ml_service
    
    result = ml_service.analyze_biometric_data(
        heart_rate=140,
        user_id=123
    )
    
    if result['alert']:
        # Guardar alerta en DB
        Alert.objects.create(**result['alert'])
"""

from typing import Dict, Any, Optional, List
from ml_predictor import HealthMonitorML
from alert_generator import AlertGenerator


class MLHealthMonitoringService:
    """
    Servicio principal de ML para monitoreo de salud de oficiales.
    
    Singleton que combina predicción ML y generación de alertas
    en una interfaz simple para consumo del backend Django.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el servicio (solo una vez por Singleton)"""
        if self._initialized:
            return
        
        print("\n" + "=" * 70)
        print("INICIALIZANDO ML HEALTH MONITORING SERVICE")
        print("=" * 70)
        
        # Inicializar componentes ML
        self.predictor = HealthMonitorML()
        self.alert_generator = AlertGenerator()
        
        # Estado
        self._initialized = True
        self._stats = {
            'total_predictions': 0,
            'total_alerts_generated': 0,
            'critical_alerts': 0,
            'high_alerts': 0,
            'medium_alerts': 0,
            'low_alerts': 0
        }
        
        print("=" * 70)
        print("ML HEALTH MONITORING SERVICE LISTO")
        print("=" * 70 + "\n")
    
    def analyze_biometric_data(self, 
                               heart_rate: float,
                               user_id: int,
                               recent_hrs: Optional[List[float]] = None,
                               timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Analiza datos biométricos y genera alerta si es necesario.
        
        Este es el método principal que el backend debe usar.
        
        Args:
            heart_rate: Frecuencia cardíaca actual (bpm)
            user_id: ID del oficial en la base de datos
            recent_hrs: Lista opcional de últimos HRs (máximo 10 valores)
            timestamp: Timestamp opcional del evento
        
        Returns:
            Dict con:
                - 'prediction': Resultado completo de predicción ML
                - 'alert': Payload de alerta (o None si no requiere)
                - 'should_notify': Boolean indicando si notificar supervisores
        
        Example:
            >>> from ML.ml_service import ml_service
            >>> 
            >>> # Cuando llega nuevo dato biométrico
            >>> result = ml_service.analyze_biometric_data(
            ...     heart_rate=140,
            ...     user_id=123
            ... )
            >>> 
            >>> # Guardar predicción
            >>> Prediction.objects.create(
            ...     user_id=result['prediction']['metadata']['user_id'],
            ...     stress_score=result['prediction']['stress_score'],
            ...     requires_alert=result['prediction']['requires_alert']
            ... )
            >>> 
            >>> # Si hay alerta, guardarla y notificar
            >>> if result['alert']:
            ...     alert_obj = Alert.objects.create(**result['alert'])
            ...     
            ...     if result['should_notify']:
            ...         notify_supervisors(alert_obj)
        """
        # Validar inputs
        if not isinstance(heart_rate, (int, float)) or heart_rate <= 0:
            raise ValueError(f"heart_rate debe ser un número positivo, recibido: {heart_rate}")
        
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"user_id debe ser un entero positivo, recibido: {user_id}")
        
        # 1. Predicción ML
        prediction = self.predictor.predict(
            heart_rate=heart_rate,
            recent_hrs=recent_hrs,
            user_id=user_id
        )
        
        # Actualizar estadísticas
        self._stats['total_predictions'] += 1
        
        # 2. Generar alerta si es necesario
        alert = None
        should_notify = False
        
        if prediction['requires_alert']:
            alert = self.alert_generator.generate_alert(
                prediction_result=prediction,
                user_id=user_id,
                timestamp=timestamp
            )
            
            if alert:
                self._stats['total_alerts_generated'] += 1
                
                # Actualizar estadísticas por severidad
                severity = alert['severity']
                if severity == 'CRITICAL':
                    self._stats['critical_alerts'] += 1
                    should_notify = True  # Siempre notificar críticos
                elif severity == 'HIGH':
                    self._stats['high_alerts'] += 1
                    should_notify = True  # Siempre notificar altos
                elif severity == 'MEDIUM':
                    self._stats['medium_alerts'] += 1
                    should_notify = False  # No notificar medios (solo guardar)
                elif severity == 'LOW':
                    self._stats['low_alerts'] += 1
                    should_notify = False
        
        # 3. Construir respuesta
        result = {
            'prediction': prediction,
            'alert': alert,
            'should_notify': should_notify,
            'metadata': {
                'analysis_timestamp': timestamp,
                'ml_version': '1.0',
                'service': 'MLHealthMonitoringService'
            }
        }
        
        return result
    
    def batch_analyze(self, 
                     data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analiza múltiples registros biométricos en lote.
        
        Útil para procesar datos históricos o múltiples usuarios.
        
        Args:
            data_list: Lista de dicts con estructura:
                [
                    {'heart_rate': 75, 'user_id': 1, 'recent_hrs': [...], 'timestamp': '...'},
                    {'heart_rate': 140, 'user_id': 2},
                    ...
                ]
        
        Returns:
            Lista de resultados de análisis (mismo formato que analyze_biometric_data)
        
        Example:
            >>> batch_data = [
            ...     {'heart_rate': 75, 'user_id': 1},
            ...     {'heart_rate': 185, 'user_id': 2},
            ...     {'heart_rate': 130, 'user_id': 3}
            ... ]
            >>> 
            >>> results = ml_service.batch_analyze(batch_data)
            >>> 
            >>> # Procesar resultados
            >>> for result in results:
            ...     if result.get('error'):
            ...         # Manejar error
            ...         continue
            ...     
            ...     if result['alert']:
            ...         # Guardar alerta
            ...         Alert.objects.create(**result['alert'])
        """
        results = []
        
        for data in data_list:
            try:
                # Validar que tenga los campos mínimos
                if 'heart_rate' not in data or 'user_id' not in data:
                    results.append({
                        'error': 'Missing required fields: heart_rate and user_id',
                        'data': data
                    })
                    continue
                
                # Analizar
                result = self.analyze_biometric_data(
                    heart_rate=data['heart_rate'],
                    user_id=data['user_id'],
                    recent_hrs=data.get('recent_hrs'),
                    timestamp=data.get('timestamp')
                )
                
                results.append(result)
                
            except Exception as e:
                # Capturar errores individuales sin detener el batch
                results.append({
                    'error': str(e),
                    'data': data
                })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estadísticas del servicio ML.
        
        Útil para monitoreo y debugging.
        
        Returns:
            Dict con estadísticas de uso del servicio
        """
        total_alerts = self._stats['total_alerts_generated']
        
        stats = {
            'total_predictions': self._stats['total_predictions'],
            'total_alerts_generated': total_alerts,
            'alerts_by_severity': {
                'CRITICAL': self._stats['critical_alerts'],
                'HIGH': self._stats['high_alerts'],
                'MEDIUM': self._stats['medium_alerts'],
                'LOW': self._stats['low_alerts']
            },
            'alert_rate': (
                (total_alerts / self._stats['total_predictions'] * 100) 
                if self._stats['total_predictions'] > 0 else 0
            ),
            'critical_rate': (
                (self._stats['critical_alerts'] / total_alerts * 100)
                if total_alerts > 0 else 0
            ),
            'service_status': 'operational' if self._initialized else 'not_initialized',
            'ml_models_loaded': {
                'predictor': bool(self.predictor),
                'alert_generator': bool(self.alert_generator)
            }
        }
        
        return stats
    
    def reset_statistics(self):
        """Reinicia las estadísticas del servicio"""
        self._stats = {
            'total_predictions': 0,
            'total_alerts_generated': 0,
            'critical_alerts': 0,
            'high_alerts': 0,
            'medium_alerts': 0,
            'low_alerts': 0
        }
        print("Estadísticas reiniciadas")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre los modelos ML cargados.
        
        Útil para verificar versiones y configuración.
        """
        info = {
            'predictor_info': self.predictor.get_model_info(),
            'alert_thresholds': self.alert_generator.thresholds,
            'service_version': '1.0',
            'initialized': self._initialized
        }
        
        return info
    
    def update_alert_thresholds(self, new_thresholds: Dict[str, float]):
        """
        Actualiza los umbrales del generador de alertas.
        
        Args:
            new_thresholds: Dict con nuevos valores
        """
        self.alert_generator.update_thresholds(new_thresholds)
        print(f"Umbrales de alertas actualizados")


# Singleton global para uso en Django
ml_service = MLHealthMonitoringService()


# Ejemplo de uso y testing
if __name__ == "__main__":
    import json
    
    print("\n" + "=" * 70)
    print("ML HEALTH MONITORING SERVICE - TEST DE INTEGRACIÓN")
    print("=" * 70)
    
    # El servicio ya está inicializado (singleton)
    service = ml_service
    
    print("\nPRUEBA 1: Análisis Individual")
    print("─" * 70)
    
    # Caso normal
    result1 = service.analyze_biometric_data(
        heart_rate=75,
        user_id=1
    )
    
    print(f"\nUsuario 1 - HR: 75 bpm")
    print(f"   • Requiere alerta: {result1['prediction']['requires_alert']}")
    print(f"   • Estrés: {result1['prediction']['stress_score']:.1f}/100")
    print(f"   • Alerta generada: {'SÍ' if result1['alert'] else 'NO'}")
    print(f"   • Notificar supervisores: {'SÍ' if result1['should_notify'] else 'NO'}")
    
    # Caso crítico
    result2 = service.analyze_biometric_data(
        heart_rate=185,
        user_id=2,
        recent_hrs=[150, 160, 170, 175, 180, 182, 183, 184, 185, 185]
    )
    
    print(f"\nUsuario 2 - HR: 185 bpm (CRÍTICO)")
    print(f"   • Requiere alerta: {result2['prediction']['requires_alert']}")
    print(f"   • Severidad: {result2['prediction']['severity']}")
    print(f"   • Estrés: {result2['prediction']['stress_score']:.1f}/100")
    if result2['alert']:
        print(f"   • Tipo de alerta: {result2['alert']['alert_type']}")
        print(f"   • Mensaje: {result2['alert']['message'][:80]}...")
        print(f"   • Acción inmediata: {result2['alert']['requires_immediate_action']}")
        print(f"   • Notificar supervisores: {'SÍ' if result2['should_notify'] else 'NO'}")
    
    print("\n" + "─" * 70)
    print("PRUEBA 2: Análisis por Lotes")
    print("─" * 70)
    
    batch_data = [
        {'heart_rate': 75, 'user_id': 10},
        {'heart_rate': 130, 'user_id': 11},
        {'heart_rate': 195, 'user_id': 12},
        {'heart_rate': 35, 'user_id': 13},
        {'heart_rate': 90, 'user_id': 14}
    ]
    
    batch_results = service.batch_analyze(batch_data)
    
    print(f"\nResultados del batch:")
    print(f"   • Total procesados: {len(batch_results)}")
    
    alerts_generated = sum(1 for r in batch_results if r.get('alert') is not None)
    critical_alerts = sum(
        1 for r in batch_results 
        if r.get('alert') and r['alert']['severity'] == 'CRITICAL'
    )
    should_notify_count = sum(1 for r in batch_results if r.get('should_notify', False))
    
    print(f"   • Alertas generadas: {alerts_generated}")
    print(f"   • Alertas críticas: {critical_alerts}")
    print(f"   • Requieren notificación: {should_notify_count}")
    
    print("\n   Detalle:")
    for i, result in enumerate(batch_results, 1):
        data = batch_data[i-1]
        if result.get('error'):
            print(f"   {i}. Usuario {data['user_id']} - ERROR: {result['error']}")
        else:
            alert_status = "Normal"
            if result['alert']:
                severity = result['alert']['severity']
                alert_status = f"{severity}"
            
            print(f"   {i}. Usuario {data['user_id']} - HR: {data['heart_rate']} bpm - {alert_status}")
    
    print("\n" + "─" * 70)
    print("ESTADÍSTICAS DEL SERVICIO")
    print("─" * 70)
    
    stats = service.get_statistics()
    
    print(f"\nMétricas generales:")
    print(f"   • Total de predicciones: {stats['total_predictions']}")
    print(f"   • Total de alertas: {stats['total_alerts_generated']}")
    print(f"   • Tasa de alertas: {stats['alert_rate']:.1f}%")
    print(f"   • Tasa de alertas críticas: {stats['critical_rate']:.1f}%")
    
    print(f"\nAlertas por severidad:")
    for severity, count in stats['alerts_by_severity'].items():
        print(f"   • {severity}: {count}")
    
    print(f"\nEstado del servicio:")
    print(f"   • Estado: {stats['service_status']}")
    print(f"   • Predictor cargado: {stats['ml_models_loaded']['predictor']}")
    print(f"   • Alert generator cargado: {stats['ml_models_loaded']['alert_generator']}")
    
    print("\n" + "─" * 70)
    print("INFORMACIÓN DE MODELOS")
    print("─" * 70)
    
    model_info = service.get_model_info()
    
    print(f"\nPredictor ML:")
    print(f"   • Features: {model_info['predictor_info']['num_features']}")
    print(f"   • Umbrales HR críticos: "
          f"{model_info['predictor_info']['hr_thresholds']['critical_low']}-"
          f"{model_info['predictor_info']['hr_thresholds']['critical_high']} bpm")
    
    print(f"\nUmbrales de Alertas:")
    print(f"   • HR crítico bajo: {model_info['alert_thresholds']['hr_critical_low']} bpm")
    print(f"   • HR crítico alto: {model_info['alert_thresholds']['hr_critical_high']} bpm")
    print(f"   • Estrés alto: {model_info['alert_thresholds']['stress_high']}")
    print(f"   • Estrés crítico: {model_info['alert_thresholds']['stress_critical']}")
    
    print("\nTest de integración completado exitosamente")
    print("=" * 70 + "\n")
    
    # Ejemplo de código para Django
    print("\n" + "=" * 70)
    print("EJEMPLO DE USO DESDE DJANGO BACKEND")
    print("=" * 70)
    
    example_code = '''
# En tu views.py o services.py de Django

from ML.ml_service import ml_service

def process_biometric_data(user_id, heart_rate, timestamp=None):
    """
    Procesa un nuevo dato biométrico de un oficial
    """
    # Obtener histórico reciente del usuario (opcional pero recomendado)
    recent_records = BiometricRecord.objects.filter(
        user_id=user_id
    ).order_by('-timestamp')[:10].values_list('heart_rate', flat=True)
    
    # Análisis ML
    result = ml_service.analyze_biometric_data(
        heart_rate=heart_rate,
        user_id=user_id,
        recent_hrs=list(recent_records),
        timestamp=timestamp
    )
    
    # Guardar predicción ML en DB
    prediction_obj = MLPrediction.objects.create(
        user_id=user_id,
        heart_rate=heart_rate,
        stress_score=result['prediction']['stress_score'],
        stress_level=result['prediction']['stress_level'],
        requires_alert=result['prediction']['requires_alert'],
        alert_probability=result['prediction']['alert_probability'],
        is_anomaly=result['prediction']['is_anomaly'],
        metadata=result['prediction']['metadata']
    )
    
    # Si hay alerta, guardarla y notificar
    if result['alert']:
        alert_obj = Alert.objects.create(**result['alert'])
        
        # Notificar supervisores si es necesario
        if result['should_notify']:
            notify_supervisors(alert_obj)
            
            # Para alertas críticas, enviar notificación urgente
            if alert_obj.severity == 'CRITICAL':
                send_urgent_notification(alert_obj)
    
    return result

# Uso en un endpoint API
@api_view(['POST'])
def receive_biometric_data(request):
    """
    Endpoint para recibir datos del smartwatch
    """
    user_id = request.data.get('user_id')
    heart_rate = request.data.get('heart_rate')
    
    # Procesar con ML
    result = process_biometric_data(user_id, heart_rate)
    
    return Response({
        'status': 'processed',
        'requires_alert': result['prediction']['requires_alert'],
        'stress_score': result['prediction']['stress_score'],
        'alert_generated': bool(result['alert'])
    })
'''
    
    print(example_code)
    print("=" * 70)
