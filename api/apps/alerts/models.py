from django.db import models

ALERT_LEVEL_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Critical', 'Critical'),
]

ALERT_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Acknowledged', 'Acknowledged'),
    ('Resolved', 'Resolved'),
    ('Dismissed', 'Dismissed'),
]


class AlertType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    default_level = models.CharField(max_length=20, choices=ALERT_LEVEL_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = 'alerts'
        db_table = 'alert_types'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class Alert(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='alerts')
    type = models.ForeignKey(AlertType, on_delete=models.CASCADE, related_name='alerts')
    level = models.CharField(max_length=20, choices=ALERT_LEVEL_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='Pending', db_index=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='acknowledged_alerts'
    )
    resolution_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'alerts'
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['level', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]

    def __str__(self):
        return f"{self.type.name} - {self.level} ({self.status})"
