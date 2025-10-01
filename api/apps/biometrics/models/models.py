from django.db import models
from apps.users.models import User

# Create your models here.

class MetricType(models.Model):
    metric_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=20, blank=True)

    class Meta:
        app_label = 'biometrics'

    def __str__(self):
        return self.type_name

class Biometric(models.Model):
    biometric_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE)
    metric_value = models.DecimalField(max_digits=10, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'biometrics'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.metric_type}: {self.metric_value}"
