from django.db import models


# Importar modelos ML
from .ml_models import MLPrediction, MLAlert


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
