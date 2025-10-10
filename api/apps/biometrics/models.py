from django.db import models

# Create your models here.

class MetricType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, blank=True)

    class Meta:
        app_label = 'biometrics'

    def __str__(self):
        return self.name

class BiometricRecord(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=3)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'biometrics'
        indexes = [
            models.Index(fields=['user', 'recorded_at']),
            models.Index(fields=['metric_type', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.metric_type}: {self.value}"