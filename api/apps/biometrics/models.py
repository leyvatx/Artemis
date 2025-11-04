from django.db import models
from django.core.validators import MinValueValidator

class MetricType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, blank=True)
    min_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = 'biometrics'
        db_table = 'metric_types'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.unit})"


class BiometricRecord(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='biometric_records')
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE, related_name='records')
    value = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'biometrics'
        db_table = 'biometric_records'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user', 'recorded_at']),
            models.Index(fields=['metric_type', 'recorded_at']),
            models.Index(fields=['user', 'metric_type', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.user.name} - {self.metric_type.name}: {self.value} {self.metric_type.unit}"
