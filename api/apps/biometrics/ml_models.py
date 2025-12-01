"""
ML Models for Biometric Predictions

Este módulo define los modelos de Django para almacenar las predicciones
del sistema de Machine Learning basado en datos de BPM.
"""

from django.db import models


class MLPrediction(models.Model):
    """
    Almacena predicciones del sistema ML para cada lectura de BPM.
    
    Estas predicciones se generan automáticamente cuando llega un nuevo
    dato de BPM desde el ESP32, sin interrumpir el flujo normal.
    """
    
    STRESS_LEVEL_CHOICES = [
        ('Muy Bajo', 'Muy Bajo'),
        ('Bajo', 'Bajo'),
        ('Moderado', 'Moderado'),
        ('Alto', 'Alto'),
        ('Muy Alto', 'Muy Alto'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.AutoField(primary_key=True)
    
    # Relación con el BPM que generó esta predicción
    bpm = models.OneToOneField(
        'biometrics.BPM',
        on_delete=models.CASCADE,
        related_name='ml_prediction'
    )
    
    # Usuario (denormalizado para queries más rápidas)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='ml_predictions'
    )
    
    # Predicción de estrés
    stress_score = models.FloatField(
        help_text="Score de estrés calculado por ML (0-100)"
    )
    stress_level = models.CharField(
        max_length=20,
        choices=STRESS_LEVEL_CHOICES,
        db_index=True,
        help_text="Nivel de estrés clasificado"
    )
    
    # Predicción de alerta
    requires_alert = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Si el modelo ML recomienda generar una alerta"
    )
    alert_probability = models.FloatField(
        help_text="Probabilidad de que se requiera alerta (0.0-1.0)"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        db_index=True,
        help_text="Severidad clasificada por el modelo ML"
    )
    
    # Detección de anomalías
    is_anomaly = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Si se detectó una anomalía en el patrón cardíaco"
    )
    anomaly_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Score de anomalía del Isolation Forest"
    )
    
    # Información contextual
    hr_zone = models.CharField(
        max_length=50,
        help_text="Zona cardíaca clasificada (ej: Zone 3 - Moderada)"
    )
    hr_variability = models.FloatField(
        null=True,
        blank=True,
        help_text="Variabilidad de la frecuencia cardíaca"
    )
    
    # Metadatos ML (almacenados como JSON)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadatos adicionales de la predicción ML"
    )
    
    # Estado de resolución (para predicciones que requieren atención)
    STATUS_CHOICES = [
        ('Pending', 'Pendiente'),
        ('Acknowledged', 'Reconocida'),
        ('Resolved', 'Resuelta'),
        ('Dismissed', 'Descartada'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        db_index=True,
        help_text="Estado de la predicción"
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se resolvió"
    )
    
    resolved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_predictions',
        help_text="Usuario que resolvió la predicción"
    )
    
    resolution_notes = models.TextField(
        blank=True,
        help_text="Notas de resolución/justificación"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        app_label = 'biometrics'
        db_table = 'ml_predictions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'requires_alert']),
            models.Index(fields=['stress_level', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
        ]
    
    def __str__(self):
        return f"MLPrediction(user={self.user_id}, stress={self.stress_score:.1f}, alert={self.requires_alert})"


class MLAlert(models.Model):
    """
    Alertas generadas automáticamente por el sistema ML.
    
    Estas alertas se crean cuando el modelo ML detecta situaciones
    que requieren atención (estrés alto, anomalías, BPM crítico).
    """
    
    ALERT_TYPE_CHOICES = [
        ('HR_CRITICAL_LOW', 'Frecuencia Cardíaca Críticamente Baja'),
        ('HR_CRITICAL_HIGH', 'Frecuencia Cardíaca Críticamente Alta'),
        ('HR_ZERO', 'Sin Señal de Frecuencia Cardíaca'),
        ('STRESS_CRITICAL', 'Estrés Crítico'),
        ('STRESS_HIGH_RISK', 'Alto Riesgo de Estrés'),
        ('HR_ABNORMALLY_HIGH', 'Frecuencia Cardíaca Anormalmente Alta'),
        ('HR_ABNORMALLY_LOW', 'Frecuencia Cardíaca Anormalmente Baja'),
        ('STRESS_ELEVATED', 'Estrés Elevado'),
        ('HR_SUSTAINED_ELEVATED', 'Frecuencia Cardíaca Elevada Sostenida'),
        ('HR_RAPID_FLUCTUATION', 'Fluctuaciones Rápidas en FC'),
        ('ANOMALY_DETECTED', 'Anomalía Detectada'),
        ('ML_PREDICTION_ALERT', 'Alerta Predictiva ML'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Acknowledged', 'Acknowledged'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
    ]
    
    id = models.AutoField(primary_key=True)
    
    # Usuario afectado
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='ml_alerts'
    )
    
    # Predicción ML que generó esta alerta
    prediction = models.ForeignKey(
        MLPrediction,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    
    # Tipo y clasificación
    alert_type = models.CharField(
        max_length=50,
        choices=ALERT_TYPE_CHOICES,
        db_index=True
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        db_index=True
    )
    
    # Mensaje y acción
    message = models.TextField(
        help_text="Mensaje descriptivo de la alerta"
    )
    action_required = models.TextField(
        help_text="Acción recomendada para esta alerta"
    )
    
    # Datos biométricos en el momento de la alerta
    heart_rate = models.FloatField()
    stress_score = models.FloatField()
    stress_level = models.CharField(max_length=20)
    
    # Flags
    requires_immediate_action = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Si requiere acción inmediata (CRITICAL/HIGH)"
    )
    is_anomaly = models.BooleanField(default=False)
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        db_index=True
    )
    
    # Gestión de alerta
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_ml_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Metadatos
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadatos adicionales de la alerta ML"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'biometrics'
        db_table = 'ml_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['user', 'requires_immediate_action']),
        ]
    
    def __str__(self):
        return f"MLAlert({self.alert_type} - {self.severity} - {self.status})"
