from django.db import models


class BPM(models.Model):
    """Simple BPM sensor readings table.

    Fields:
      - id: Auto primary key
      - user: ForeignKey to users.User
      - value: Float value of BPM
      - created_at: Timestamp of BPM reading
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bpms')
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'biometrics'
        db_table = 'bpm'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"BPM({self.user_id}) = {self.value}"


class MLPrediction(models.Model):
    """ML predictions for biometric data analysis.
    
    Stores the results from the ML service analyzing BPM readings.
    Used to track stress levels, anomalies, and alert requirements.
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
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ml_predictions')
    bpm_record = models.ForeignKey(BPM, on_delete=models.CASCADE, related_name='ml_predictions')
    
    # ML prediction results
    stress_score = models.FloatField(help_text='Stress score from 0-100')
    stress_level = models.CharField(max_length=20, choices=STRESS_LEVEL_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    requires_alert = models.BooleanField(default=False, db_index=True)
    alert_probability = models.FloatField(help_text='Probability of requiring alert (0.0-1.0)')
    is_anomaly = models.BooleanField(default=False, db_index=True)
    
    # Additional ML metadata
    hr_zone = models.CharField(max_length=50, blank=True)
    ml_metadata = models.JSONField(default=dict, blank=True)
    
    # Alert association (if created)
    alert = models.ForeignKey(
        'alerts.Alert',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_predictions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        app_label = 'biometrics'
        db_table = 'ml_predictions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['requires_alert', 'created_at']),
            models.Index(fields=['is_anomaly', 'created_at']),
            models.Index(fields=['stress_level', 'created_at']),
        ]
    
    def __str__(self):
        return f"MLPrediction({self.user_id}) - Stress: {self.stress_score:.1f}/100 - {self.stress_level}"
