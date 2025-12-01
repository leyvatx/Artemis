# Guía Rápida - Módulo ML Artemis

## Lo que se ha completado

### 1. Notebook de Entrenamiento Completo

- `model_training.ipynb` con 15 secciones:
  1. Carga de datos
  2. Exploración de datos
  3. Limpieza y preprocesamiento
  4. Feature engineering (6 features desde HR)
  5. Detección de patrones de estrés (SRS FR-004)
  6. Visualización de patrones de estrés
  7. Actualización de features (9 features extendidas)
  8. Visualización comprehensiva de HR
  9. Modelo Isolation Forest (anomalías)
  10. Modelo DBSCAN (clustering)
  11. Visualización de anomalías
  12. Sistema de clasificación de alertas (5 niveles)
  13. Modelo Random Forest (predicción)
  14. Visualización de Random Forest
  15. Guardado de modelos
  16. Resumen y conclusiones
  17. Guía de integración con Django

### 2. Módulo de Predicción para Backend

- `ml_predictor.py`: Clase `HealthMonitorML` lista para usar
  - Método `predict()` - Predicción individual
  - Método `batch_predict()` - Predicción por lotes
  - Método `get_model_info()` - Info de modelos
  - Validación automática de inputs
  - Cálculo automático de features
  - Detección de estrés integrada

### 3. Documentación Completa

- `README_ML.md`: Guía detallada con:
  - Descripción de responsabilidades ML vs Backend
  - Ejemplos de uso desde Django
  - Estructura de respuesta del predictor
  - Casos de uso (monitoreo real-time, análisis retrospectivo, API endpoints)
  - Configuración inicial en Django
  - Tests de integración

## Tu Responsabilidad (Solo ML)

Como desarrollador del módulo ML, tú te encargas ÚNICAMENTE de:

1. Detección de Estrés - Calcular stress_score (0-100)
2. Detección de Anomalías - Identificar HRs anormales
3. Clasificación de Severidad - CRITICAL/HIGH/MEDIUM/LOW
4. Predicción - Probabilidad de requerir alerta
5. Retornar Datos - Dict estructurado para el backend

## NO es tu responsabilidad

El equipo de backend se encarga de:

- Guardar alertas en PostgreSQL
- Enviar notificaciones a supervisores
- Mostrar alertas en panel web
- Gestionar estados de alertas

## Archivos Entregables

```
ML/
├── model_training.ipynb              ← Notebook completo (ejecutar para generar modelos)
│
├── ml_service.py                     ← SERVICIO PRINCIPAL para backend
├── ml_predictor.py                   ← Módulo de predicción ML
├── alert_generator.py                ← Generador de alertas automáticas
│
├── README_ML.md                      ← Documentación completa
├── QUICK_START.md                    ← Este archivo
├── requirements.txt                  ← Dependencias Python
├── processed_health_data.csv         ← Dataset procesado
│
└── Modelos generados (después de ejecutar notebook):
    ├── model_isolation_forest.pkl
    ├── model_random_forest.pkl
    ├── model_dbscan.pkl
    ├── model_scaler.pkl
    ├── model_scaler_rf.pkl
    └── model_config.pkl
```

## Cómo Usar (Para Ti)

### Paso 1: Ejecutar el Notebook (Una sola vez)

```bash
cd ML/
jupyter notebook model_training.ipynb
```

En Jupyter:

- `Cell > Run All` para ejecutar todo
- Esto generará los 6 archivos `.pkl` necesarios
- Tardará unos minutos (depende del tamaño del dataset)

### Paso 2: Probar el Predictor

```bash
# Probar el predictor individual
cd ML/
python ml_predictor.py

# Probar el generador de alertas
python alert_generator.py

# Probar el servicio completo (RECOMENDADO)
python ml_service.py
```

Esto ejecutará casos de prueba y mostrará resultados.

### Paso 3: Entregar al Backend

Comparte con el equipo backend:

1. La carpeta `ML/` completa (con los `.pkl` generados)
2. `README_ML.md` para que sepan cómo integrarlo
3. Les dices: **"Usen `ml_service.py` - está todo documentado en el README"**

El backend debe usar `ml_service` así:

```python
from ML.ml_service import ml_service

# Cuando llega nuevo HR del smartwatch
result = ml_service.analyze_biometric_data(
    heart_rate=140,
    user_id=123
)

# Si hay alerta, guardarla en DB
if result['alert']:
    Alert.objects.create(**result['alert'])

    # Notificar si es necesario
    if result['should_notify']:
        notify_supervisors(result['alert'])
```

## Test Rápido

```python
# En consola Python (dentro de ML/)

# OPCIÓN 1: Usar el servicio completo (RECOMENDADO)
from ml_service import ml_service

result = ml_service.analyze_biometric_data(
    heart_rate=140,
    user_id=123
)

print(f"Alerta: {result['alert']}")
print(f"Notificar: {result['should_notify']}")

# OPCIÓN 2: Usar solo el predictor
from ml_predictor import HealthMonitorML

predictor = HealthMonitorML()

# Caso normal
result = predictor.predict(heart_rate=75)
print(f"HR 75: Alerta={result['requires_alert']}, Estrés={result['stress_score']:.1f}")

# Caso crítico
result = predictor.predict(heart_rate=185)
print(f"HR 185: Alerta={result['requires_alert']}, Severidad={result['severity']}")
```

## Métricas del Sistema

Después de ejecutar el notebook, verás:

- **Dataset**: ~10,000 muestras analizadas
- **Features**: 9 características calculadas desde HR
- **Modelos**: 3 modelos entrenados (IF, RF, DBSCAN)
- **Accuracy**: ~85-95% en test set (depende del dataset)
- **Gráficos**: 4 visualizaciones PNG generadas

## Mantenimiento Futuro

### Reentrenar Modelos

Si llegan nuevos datos:

1. Agregar datos a `Dataset/unclean_smartwatch_health_data.csv`
2. Volver a ejecutar `model_training.ipynb` completo
3. Los `.pkl` se actualizan automáticamente
4. Backend debe reiniciar Django para cargar nuevos modelos

### Ajustar Umbrales

Si necesitas cambiar umbrales de estrés/alertas:

1. Editar en el notebook (sección 13: model_config)
2. Re-ejecutar desde esa sección en adelante
3. Los cambios se guardan en `model_config.pkl`

## Soporte al Equipo Backend

Si el backend tiene dudas, indícales:

1. **Instalación**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Uso Básico** (ver `README_ML.md` sección "Inicio Rápido"):

   ```python
   from ML.ml_service import ml_service

   # Análisis completo (predicción + alerta)
   result = ml_service.analyze_biometric_data(
       heart_rate=120,
       user_id=officer_id
   )

   # Guardar predicción
   Prediction.objects.create(
       user_id=officer_id,
       stress_score=result['prediction']['stress_score'],
       requires_alert=result['prediction']['requires_alert']
   )

   # Si hay alerta, guardarla
   if result['alert']:
       Alert.objects.create(**result['alert'])

       # Notificar si es crítico o alto
       if result['should_notify']:
           notify_supervisors(result['alert'])
   ```

3. **Ejemplos Completos**: Ver sección "Ejemplos de Casos de Uso" en `README_ML.md`

4. **Pruebas**: Ejecutar `python ml_service.py` para ver ejemplos funcionando

## Cumplimiento SRS

Este módulo cumple con:

- **FR-004: Risk Detection and Prediction**

  - "The Machine Learning module must process biometric data to detect patterns that indicate stress on the officers"
  - Procesa HR
  - Detecta patrones de estrés
  - Calcula stress_score
  - Identifica alto riesgo

- **FR-006: Automatic Alert Activation** (parcial, lo demás es del backend)
  - "The system must automatically generate an alert when a high risk of stress is detected, or when the HR is abnormally high or zero"
  - Detecta HR anormalmente alta (>180 bpm)
  - Detecta HR anormalmente baja (<40 bpm)
  - Detecta alto riesgo de estrés (score >70)
  - Retorna `requires_alert=True/False`
  - Backend genera la alerta en DB (no es ML)

## Resumen para Presentación

**Tu contribución**:

- Modelo ML que predice estrés basado solo en HR
- 3 algoritmos: Isolation Forest (anomalías), DBSCAN (clustering), Random Forest (predicción)
- 9 features calculadas automáticamente
- Módulo Python listo para integrar con Django
- Documentación completa para el equipo

**Arquitectura**:

```
Smartwatch → Backend Django → ml_predictor.predict() → ML Models
                ↓
            Guardar alerta en DB (si requires_alert=True)
                ↓
            Notificar supervisor
```

**Decisión de diseño importante**:

- ML solo hace predicciones
- Backend maneja la lógica de negocio (alertas, notificaciones)
- Separación clara de responsabilidades (Single Responsibility Principle)

Puedes entregar:

1. `model_training.ipynb` ejecutado (con outputs)
2. `ml_predictor.py` probado
3. `README_ML.md` para backend
4. Archivos `.pkl` generados

El módulo ML está completo y listo para integración.
