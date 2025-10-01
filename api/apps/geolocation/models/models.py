from django.db import models
from apps.users.models import User

# Create your models here.

class GeoLocation(models.Model):
    geolocation_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)  # Placeholder for POINT
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'geolocation'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user} at {self.location}"
