from django.db import models


class Recommendation(models.Model):
    PRIORITY_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Crítica', 'Crítica'),
    ]
    
    CATEGORY_CHOICES = [
        ('Salud', 'Salud'),
        ('Ejercicio', 'Ejercicio'),
        ('Nutrición', 'Nutrición'),
        ('Descanso', 'Descanso'),
        ('Mental', 'Salud Mental'),
        ('Otro', 'Otro'),
    ]
    
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Reconocida', 'Reconocida'),
        ('Resuelta', 'Resuelta'),
    ]
    
    recommendation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='recommendations')
    alert = models.ForeignKey('alerts.Alert', on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    message = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Otro', db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Media', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_recommendations')
    resolution_notes = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'recommendations'
        db_table = 'recommendations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['category', 'priority']),
        ]

    def __str__(self):
        return f"[{self.priority}] {self.message[:50]}"
