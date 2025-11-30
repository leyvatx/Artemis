# Módulo ML - Artemis Health Monitoring

## 📋 Descripción

Este módulo contiene el sistema de Machine Learning para detección de estrés y anomalías en oficiales basado únicamente en datos de frecuencia cardíaca (HR).

## 🎯 Responsabilidades del Módulo ML

El módulo ML **SOLO** se encarga de:

- ✅ Calcular scores de estrés (0-100)
- ✅ Detectar anomalías en HR
- ✅ Clasificar severidad de alertas
- ✅ Predecir probabilidad de requerir alerta
- ✅ Retornar datos estructurados para el backend

## ⚠️ Responsabilidades del Backend (NO incluidas aquí)

El backend Django debe encargarse de:

- ❌ Guardar alertas en la base de datos
- ❌ Enviar notificaciones a supervisores
- ❌ Mostrar alertas en el panel de supervisores
- ❌ Gestionar estado de alertas (leída/no leída, etc.)
- ❌ Almacenar histórico de predicciones

## 📁 Archivos del Módulo

```
ML/
├── model_training.ipynb          # Notebook de entrenamiento (ejecutar primero)
│
├── ml_service.py                 # ⭐ SERVICIO PRINCIPAL (usar este desde Django)
├── ml_predictor.py               # Módulo de predicción ML
├── alert_generator.py            # Generador de alertas automáticas
│
├── processed_health_data.csv     # Dataset procesado
│
├── model_isolation_forest.pkl    # Modelo de detección de anomalías
├── model_dbscan.pkl              # Modelo de clustering
├── model_random_forest.pkl       # Modelo predictivo de alertas
├── model_scaler.pkl              # Normalizador de features
├── model_scaler_rf.pkl           # Normalizador para Random Forest
├── model_config.pkl              # Configuración de modelos
│
├── README_ML.md                  # Esta documentación
├── QUICK_START.md                # Guía rápida
└── requirements.txt              # Dependencias Python
```

## 🚀 Inicio Rápido

### 1. Entrenar los Modelos (Una sola vez)

```bash
# Activar entorno virtual
cd ML/
jupyter notebook model_training.ipynb
# Ejecutar todas las celdas (Cell > Run All)
```

Esto generará todos los archivos `.pkl` necesarios.

### 2. Usar el Servicio ML desde Django (RECOMENDADO)

```python
# En tus views o servicios de Django
from ML.ml_service import ml_service

# El servicio ya está inicializado (singleton)
# Hacer análisis completo (predicción + alerta)
result = ml_service.analyze_biometric_data(
    heart_rate=120,
    user_id=officer.id
)

# result contiene:
# {
#     'prediction': {...},      # Predicción ML completa
#     'alert': {...} o None,    # Alerta generada (si aplica)
#     'should_notify': True/False  # Si notificar supervisores
# }

# Guardar predicción
Prediction.objects.create(
    user_id=officer.id,
    stress_score=result['prediction']['stress_score'],
    requires_alert=result['prediction']['requires_alert']
)

# Si hay alerta, guardarla y notificar
if result['alert']:
    alert_obj = Alert.objects.create(**result['alert'])
    
    if result['should_notify']:
        notify_supervisors(alert_obj)
```

### 3. Opción Alternativa: Usar Predictor Solo

```python
# Si solo necesitas predicción sin generación de alertas
from ML.ml_predictor import HealthMonitorML

predictor = HealthMonitorML()
prediction = predictor.predict(heart_rate=120)

# Luego tú decides qué hacer con la predicción
```

## 📊 Estructura de la Respuesta

### `predict()` retorna:

```python
{
    # Decisión principal
    'requires_alert': bool,              # ¿Necesita alerta? (sí/no)
    
    # Información de estrés
    'stress_score': float,               # Score 0-100
    'stress_level': str,                 # 'Muy Bajo', 'Bajo', 'Moderado', 'Alto', 'Muy Alto'
    
    # Clasificación de severidad
    'severity': str,                     # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    
    # Probabilidades y detección
    'alert_probability': float,          # 0.0 - 1.0
    'is_anomaly': bool,                  # ¿Es anomalía detectada?
    
    # Contexto
    'hr_zone': str,                      # Zona cardíaca (1-5)
    
    # Metadatos adicionales
    'metadata': {
        'heart_rate': float,
        'anomaly_score': float,
        'high_stress_risk': int,         # 0 o 1
        'hr_variability': float,
        'hr_elevated_sustained': int,    # 0 o 1
        'hr_rapid_changes': int,
        'user_id': int,
        'features': {...}                # Features calculadas
    }
}
```

## 🔧 Uso Avanzado

### Con historial de HR (recomendado para mejor precisión)

```python
# Si tienes los últimos 10 valores de HR del usuario
recent_hrs = [72, 75, 73, 78, 120, 118, 115, 120, 122, 120]

result = predictor.predict(
    heart_rate=120,
    recent_hrs=recent_hrs,
    user_id=officer.id
)
```

### Predicción por lotes

```python
# Para múltiples usuarios
heart_rates = [75, 130, 185, 62]
user_ids = [1, 2, 3, 4]

results = predictor.batch_predict(heart_rates, user_ids)

for result in results:
    if 'error' not in result and result['requires_alert']:
        # Procesar alerta...
        pass
```

### Información del modelo

```python
info = predictor.get_model_info()
print(f"Features usadas: {info['num_features']}")
print(f"Umbrales: {info['hr_thresholds']}")
```

## 📈 Features Calculadas

El predictor calcula automáticamente estas features a partir del HR:

1. **heart_rate**: HR actual
2. **hr_rolling_mean_5**: Media móvil de 5 valores
3. **hr_rolling_std_5**: Desviación estándar de 5 valores
4. **hr_rolling_mean_10**: Media móvil de 10 valores
5. **hr_diff_abs**: Diferencia absoluta con valor anterior
6. **hr_ratio_to_median**: Ratio con respecto a la mediana

**Features de estrés** (calculadas internamente):
- **hr_variability**: Variabilidad de HR (HRV)
- **hr_elevated_sustained**: HR elevada sostenida (>100 bpm)
- **hr_rapid_changes**: Cambios bruscos en ventana de 5 valores

## 🎯 Umbrales Configurados

### HR (Frecuencia Cardíaca)
- **Crítico bajo**: < 40 bpm
- **Crítico alto**: > 180 bpm
- **Warning bajo**: < 50 bpm
- **Warning alto**: > 150 bpm

### Stress Score
- **Muy Bajo**: 0-30
- **Bajo**: 30-50
- **Moderado**: 50-70
- **Alto**: 70-85
- **Muy Alto**: 85-100

### Zonas Cardíacas
1. **Zone 1 (Muy Baja)**: < 60 bpm
2. **Zone 2 (Baja)**: 60-100 bpm
3. **Zone 3 (Moderada)**: 100-120 bpm
4. **Zone 4 (Alta)**: 120-150 bpm
5. **Zone 5 (Muy Alta)**: > 150 bpm

## 🔍 Ejemplos de Casos de Uso

### Caso 1: Monitoreo en tiempo real

```python
# Cuando llega un nuevo dato biométrico
def on_new_biometric_data(user_id, heart_rate):
    # Obtener historial reciente del usuario
    recent_hrs = BiometricRecord.objects.filter(
        user_id=user_id
    ).order_by('-timestamp')[:10].values_list('heart_rate', flat=True)
    
    # Hacer predicción
    result = predictor.predict(
        heart_rate=heart_rate,
        recent_hrs=list(recent_hrs),
        user_id=user_id
    )
    
    # Si requiere alerta, crearla
    if result['requires_alert']:
        alert = Alert.objects.create(
            user_id=user_id,
            alert_type='STRESS' if result['stress_score'] > 70 else 'ANOMALY',
            severity=result['severity'],
            stress_score=result['stress_score'],
            heart_rate=heart_rate,
            metadata=result['metadata']
        )
        
        # Notificar según severidad
        if result['severity'] in ['CRITICAL', 'HIGH']:
            send_urgent_notification(alert)
        else:
            send_normal_notification(alert)
    
    return result
```

### Caso 2: Análisis retrospectivo

```python
# Analizar todos los datos de un día
def analyze_daily_data(user_id, date):
    records = BiometricRecord.objects.filter(
        user_id=user_id,
        timestamp__date=date
    ).order_by('timestamp')
    
    alerts_generated = 0
    high_stress_count = 0
    
    for record in records:
        result = predictor.predict(heart_rate=record.heart_rate)
        
        if result['requires_alert']:
            alerts_generated += 1
        
        if result['stress_score'] > 70:
            high_stress_count += 1
    
    return {
        'total_records': records.count(),
        'alerts_generated': alerts_generated,
        'high_stress_periods': high_stress_count,
        'avg_stress': records.aggregate(Avg('stress_score'))
    }
```

### Caso 3: Endpoint API para supervisores

```python
# En views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def check_officer_status(request):
    """
    Endpoint para que supervisores consulten estado ML de un oficial
    """
    officer_id = request.data.get('officer_id')
    
    # Obtener último HR
    latest_record = BiometricRecord.objects.filter(
        user_id=officer_id
    ).order_by('-timestamp').first()
    
    if not latest_record:
        return Response({'error': 'No data available'}, status=404)
    
    # Obtener historial
    recent_hrs = BiometricRecord.objects.filter(
        user_id=officer_id
    ).order_by('-timestamp')[:10].values_list('heart_rate', flat=True)
    
    # Predicción ML
    result = predictor.predict(
        heart_rate=latest_record.heart_rate,
        recent_hrs=list(recent_hrs),
        user_id=officer_id
    )
    
    return Response({
        'officer_id': officer_id,
        'timestamp': latest_record.timestamp,
        'ml_prediction': result,
        'recommendation': get_recommendation(result)
    })

def get_recommendation(result):
    """Genera recomendación basada en predicción ML"""
    if result['severity'] == 'CRITICAL':
        return 'Contactar inmediatamente al oficial'
    elif result['severity'] == 'HIGH':
        return 'Monitorear de cerca y verificar estado'
    elif result['stress_score'] > 70:
        return 'Considerar intervención preventiva'
    else:
        return 'Estado normal, continuar monitoreo'
```

## ⚙️ Configuración Inicial en Django

### Opción 1: Singleton Pattern (Recomendado)

```python
# En config/ml_service.py
from ML.ml_predictor import HealthMonitorML

class MLService:
    _instance = None
    _predictor = None
    
    @classmethod
    def get_predictor(cls):
        if cls._predictor is None:
            cls._predictor = HealthMonitorML()
        return cls._predictor

# Uso en cualquier parte del código
from config.ml_service import MLService

predictor = MLService.get_predictor()
result = predictor.predict(heart_rate=120)
```

### Opción 2: Inicializar en AppConfig

```python
# En apps/biometrics/apps.py
from django.apps import AppConfig

class BiometricsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.biometrics'
    
    def ready(self):
        # Cargar predictor ML al iniciar Django
        from ML.ml_predictor import HealthMonitorML
        self.ml_predictor = HealthMonitorML()
        print("✅ ML Predictor cargado")
```

## 🧪 Testing

```python
# tests/test_ml_integration.py
from django.test import TestCase
from ML.ml_predictor import HealthMonitorML

class MLPredictorTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.predictor = HealthMonitorML()
    
    def test_normal_hr(self):
        result = self.predictor.predict(heart_rate=75)
        self.assertFalse(result['requires_alert'])
        self.assertEqual(result['severity'], 'LOW')
    
    def test_critical_hr(self):
        result = self.predictor.predict(heart_rate=185)
        self.assertTrue(result['requires_alert'])
        self.assertEqual(result['severity'], 'CRITICAL')
    
    def test_stress_detection(self):
        result = self.predictor.predict(heart_rate=130)
        self.assertGreater(result['stress_score'], 0)
        self.assertIn(result['stress_level'], 
                     ['Muy Bajo', 'Bajo', 'Moderado', 'Alto', 'Muy Alto'])
```

## 📝 Notas Importantes

1. **Modelos Pre-entrenados**: Los archivos `.pkl` deben existir antes de usar `ml_predictor.py`
2. **Thread-Safe**: El predictor es seguro para usar en entornos multi-thread de Django
3. **Performance**: Cargar los modelos una sola vez al inicio, no en cada request
4. **Validación**: El predictor valida automáticamente inputs (raises ValueError si inválido)
5. **Historial Opcional**: Si no proporcionas `recent_hrs`, el predictor usa estimaciones
6. **Batch Processing**: Usa `batch_predict()` para procesar múltiples usuarios eficientemente

## 🔗 Integración con Requisitos SRS

Este módulo cumple con:

- **FR-004**: Risk Detection and Prediction
  - ✅ Procesa datos biométricos (HR)
  - ✅ Detecta patrones de estrés
  - ✅ Calcula score de estrés (0-100)
  - ✅ Identifica casos de alto riesgo

- **FR-006**: Automatic Alert Activation (parcial)
  - ✅ Detecta cuando HR es anormalmente alta/baja
  - ✅ Identifica riesgo de estrés
  - ✅ Retorna `requires_alert` para el backend
  - ❌ Backend debe crear la alerta en DB (no es responsabilidad del ML)

## 📞 Soporte

Si tienes dudas sobre la integración ML:

1. Revisa este README
2. Consulta los ejemplos en `ml_predictor.py` (sección `if __name__ == "__main__"`)
3. Ejecuta el test: `python ml_predictor.py` (dentro de la carpeta ML)

## 🔄 Actualización de Modelos

Para reentrenar los modelos con nuevos datos:

1. Agregar datos nuevos al dataset
2. Ejecutar nuevamente `model_training.ipynb` completo
3. Los archivos `.pkl` se sobrescribirán automáticamente
4. Reiniciar Django para cargar los nuevos modelos

---

**Última actualización**: 2024
**Versión**: 1.0
**Modelo base**: Isolation Forest + Random Forest + DBSCAN
