# Integración ML con Django - Artemis

## 📋 Resumen

El sistema de Machine Learning está **completamente integrado** con el backend de Django y funciona de manera **transparente** sin afectar el flujo del ESP32.

## 🔄 Flujo Automático

### Cuando el ESP32 envía datos de BPM:

```
1. ESP32 → POST /api/biometrics/bpm/
   {
     "user_id": 1,
     "value": 120
   }

2. Django valida y GUARDA el BPM ✅
   (El ESP32 recibe respuesta inmediata)

3. ML se ejecuta EN SEGUNDO PLANO 🤖
   - Obtiene histórico del usuario (últimos 10 BPM)
   - Ejecuta predicción ML
   - Calcula stress_score (0-100)
   - Detecta anomalías
   - Clasifica severidad

4. Guarda MLPrediction en BD 💾

5. Si requiere alerta → Crea MLAlert automáticamente 🚨
```

**✅ El ESP32 NUNCA se ve afectado**  
Si el ML falla, el BPM ya está guardado.

## 🗄️ Nuevos Modelos en BD

### MLPrediction

Almacena todas las predicciones ML para cada BPM.

**Campos principales:**

- `stress_score` (0-100)
- `stress_level` ("Muy Bajo", "Bajo", "Moderado", "Alto", "Muy Alto")
- `requires_alert` (Boolean)
- `severity` ("LOW", "MEDIUM", "HIGH", "CRITICAL")
- `is_anomaly` (Boolean)
- `hr_zone` (Zona cardíaca)
- `metadata` (JSON con features ML)

### MLAlert

Alertas automáticas generadas por el ML.

**Tipos de alertas:**

- `HR_CRITICAL_LOW`: BPM < 40
- `HR_CRITICAL_HIGH`: BPM > 180
- `STRESS_CRITICAL`: Estrés muy alto (>85)
- `STRESS_HIGH_RISK`: Alto riesgo (>70)
- `HR_ABNORMALLY_HIGH/LOW`: Fuera de rango normal
- `ANOMALY_DETECTED`: Patrón anormal detectado
- Y más...

**Campos principales:**

- `alert_type`: Tipo de alerta
- `severity`: "LOW", "MEDIUM", "HIGH", "CRITICAL"
- `message`: Descripción de la alerta
- `action_required`: Acción recomendada
- `status`: "Pending", "Acknowledged", "Resolved", "Dismissed"
- `requires_immediate_action`: Boolean

## 📡 Nuevos Endpoints API

### Predicciones ML

```bash
# Listar todas las predicciones
GET /api/biometrics/predictions/

# Predicciones de un usuario
GET /api/biometrics/predictions/user/{user_id}/

# Última predicción de un usuario
GET /api/biometrics/predictions/user/{user_id}/latest/

# Resumen de riesgo (últimas 24h)
GET /api/biometrics/predictions/user/{user_id}/risk-summary/?hours=24
```

**Ejemplo de respuesta (risk-summary):**

```json
{
  "user_id": 1,
  "period_hours": 24,
  "total_readings": 156,
  "avg_stress_score": 45.3,
  "high_stress_periods": 12,
  "anomalies_detected": 2,
  "pending_alerts": 3,
  "critical_alerts": 1,
  "high_alerts": 2,
  "risk_level": "HIGH"
}
```

### Alertas ML

```bash
# Listar todas las alertas
GET /api/biometrics/alerts/

# Alertas pendientes
GET /api/biometrics/alerts/pending/

# Alertas críticas
GET /api/biometrics/alerts/critical/

# Alertas de un usuario
GET /api/biometrics/alerts/user/{user_id}/

# Reconocer alerta
POST /api/biometrics/alerts/{id}/acknowledge/

# Resolver alerta
POST /api/biometrics/alerts/{id}/resolve/
{
  "resolution_notes": "Se contactó al oficial, está bien"
}
```

## 🚀 Cómo Empezar

### 1. Ejecutar migraciones

```bash
cd C:\Users\aleja\OneDrive\Desktop\Artemiss\BackupAPI\api
python manage.py makemigrations biometrics
python manage.py migrate biometrics
```

### 2. Entrenar modelos ML (OPCIONAL)

Si quieres usar ML real en lugar del mock:

```bash
cd ML/
jupyter notebook model_training.ipynb
# Ejecutar todas las celdas
```

Esto generará los archivos `.pkl` necesarios.

**Nota:** El sistema funciona perfectamente con el **Mock ML** mientras no tengas los modelos entrenados.

### 3. Probar integración

```bash
# Enviar un BPM de prueba
curl -X POST http://localhost:8000/api/biometrics/bpm/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "value": 120}'

# Ver la predicción ML generada
curl http://localhost:8000/api/biometrics/predictions/user/1/latest/

# Ver alertas pendientes
curl http://localhost:8000/api/biometrics/alerts/pending/
```

## 🎯 Umbrales y Clasificación

### Frecuencia Cardíaca

- **Crítico Bajo**: < 40 bpm → Alerta CRITICAL
- **Crítico Alto**: > 180 bpm → Alerta CRITICAL
- **Warning Bajo**: < 50 bpm → Alerta HIGH
- **Warning Alto**: > 150 bpm → Alerta HIGH
- **Normal**: 60-100 bpm

### Estrés (Score 0-100)

- **Muy Bajo**: 0-30
- **Bajo**: 30-50
- **Moderado**: 50-70
- **Alto**: 70-85 → Alerta HIGH
- **Muy Alto**: 85-100 → Alerta CRITICAL

### Zonas Cardíacas

1. **Zone 1**: < 60 bpm (Muy Baja)
2. **Zone 2**: 60-100 bpm (Baja/Normal)
3. **Zone 3**: 100-120 bpm (Moderada)
4. **Zone 4**: 120-150 bpm (Alta)
5. **Zone 5**: > 150 bpm (Muy Alta)

## 🔍 Monitoreo y Logs

El sistema registra eventos importantes:

```python
# En los logs verás:
"ML Analysis OK: BPM 123 -> Stress=65.3, Alert=False"
"ALERTA ML CREADA: STRESS_HIGH_RISK (HIGH) para usuario 5"
"NOTIFICACIÓN REQUERIDA: Alerta 45 (CRITICAL) para usuario 2"
```

Los logs están en nivel INFO/WARNING/CRITICAL según la importancia.

## 🛡️ Seguridad y Robustez

### ✅ El sistema está diseñado para NO ROMPER NADA:

1. **ESP32 protegido**: El ML se ejecuta DESPUÉS de guardar el BPM
2. **Errores aislados**: Si ML falla, solo se loguea el error
3. **Mock automático**: Si los modelos no existen, usa predictor básico
4. **Transacciones atómicas**: Las alertas se guardan correctamente o no se guardan
5. **Lazy loading**: Los modelos ML se cargan solo cuando se necesitan

### ❌ Lo que NO debes hacer:

- ❌ NO elimines la tabla `bpm` (romperías el ESP32)
- ❌ NO cambies los campos `user_id` o `value` del BPMSerializer
- ❌ NO bloquees el endpoint `/api/biometrics/bpm/`
- ❌ NO agregues campos de otros biométricos (SpO2, presión, etc.)

## 📊 Dashboard de Supervisor (Ejemplo)

```javascript
// Obtener resumen de todos los oficiales
async function getOfficersRiskSummary() {
  const officers = await fetch("/api/users/").then((r) => r.json());

  for (const officer of officers) {
    const risk = await fetch(
      `/api/biometrics/predictions/user/${officer.id}/risk-summary/?hours=8`
    ).then((r) => r.json());

    console.log(
      `${officer.name}: Riesgo ${risk.risk_level}, Estrés promedio ${risk.avg_stress_score}`
    );

    if (risk.critical_alerts > 0) {
      alert(
        `⚠️ ${officer.name} tiene ${risk.critical_alerts} alertas críticas!`
      );
    }
  }
}

// Obtener alertas pendientes en tiempo real
async function getPendingAlerts() {
  const alerts = await fetch("/api/biometrics/alerts/pending/").then((r) =>
    r.json()
  );

  // Mostrar alertas críticas primero
  alerts
    .filter((a) => a.severity === "CRITICAL")
    .forEach((alert) => {
      showNotification({
        title: `🚨 ALERTA CRÍTICA: ${alert.user_name}`,
        body: alert.message,
        action: alert.action_required,
      });
    });
}
```

## 🔧 Personalización

### Cambiar umbrales de alerta

Edita `ML/ml_service.py` en la clase `MockAlertGenerator` o `ML/alert_generator.py` si usas ML real:

```python
self.thresholds = {
    'hr_critical_low': 40,      # Cambiar según necesidad
    'hr_critical_high': 180,    # Cambiar según necesidad
    'stress_critical': 85,
    'stress_high': 70,
    # ...
}
```

### Agregar nuevos tipos de alertas

Edita `apps/biometrics/ml_models.py`:

```python
ALERT_TYPE_CHOICES = [
    # ... existentes
    ('NUEVA_ALERTA', 'Descripción de Nueva Alerta'),
]
```

## 📞 Soporte

Si tienes problemas:

1. ✅ Verifica que las migraciones se ejecutaron
2. ✅ Revisa los logs de Django
3. ✅ Prueba con el Mock ML primero
4. ✅ Verifica que el ESP32 sigue funcionando
5. ✅ Consulta esta documentación

## 📚 Archivos Importantes

```
BackupAPI/api/
├── apps/biometrics/
│   ├── models.py              # Modelo BPM original
│   ├── ml_models.py           # ← NUEVO: Modelos ML
│   ├── ml_service.py          # ← NUEVO: Servicio ML
│   ├── views.py               # ← MODIFICADO: Integración ML
│   ├── serializers.py         # ← MODIFICADO: Serializers ML
│   └── urls.py                # ← MODIFICADO: Rutas ML
│
└── ML/
    ├── ml_predictor.py        # Predictor ML original
    ├── alert_generator.py     # Generador de alertas original
    ├── ml_service.py          # Servicio ML original (no usado)
    ├── model_*.pkl            # Modelos entrenados
    └── INTEGRACION_DJANGO.md  # ← Esta documentación
```

## ✨ Beneficios de esta Integración

1. ✅ **No rompe nada existente**
2. ✅ **ESP32 sigue funcionando igual**
3. ✅ **Solo usa BPM** (como pediste)
4. ✅ **Detección automática de estrés**
5. ✅ **Alertas inteligentes**
6. ✅ **Resúmenes de riesgo**
7. ✅ **API REST completa**
8. ✅ **Logs detallados**
9. ✅ **Robusto ante errores**
10. ✅ **Fácil de monitorear**

---

**¡El sistema está listo para usar! 🚀**
