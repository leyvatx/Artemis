from django.db import models

# Create your models here.

class AlertType(models.Model):
    LEVEL_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    alert_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50, unique=True)
    default_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    def __str__(self):
        return self.type_name

class Alert(models.Model):
    LEVEL_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Acknowledged', 'Acknowledged'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
    ]
    alert_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE)
    alert_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    alert_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)  # Placeholder for POINT
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    resolution_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Alert for {self.user} - {self.alert_type}"
