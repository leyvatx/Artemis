from django.db import models

# Create your models here.

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

    class Meta:
        app_label = 'alerts'

    def __str__(self):
        return self.name

class Alert(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    type = models.ForeignKey(AlertType, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=ALERT_LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='Pending')
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    resolution_notes = models.TextField(blank=True)

    class Meta:
        app_label = 'alerts'

    def __str__(self):
        return f"{self.type.name} - {self.level} - {self.user.name}"
