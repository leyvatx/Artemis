from django.db import models
# from django.contrib.gis.db import models as gis_models  # Para PostGIS
from django.core.validators import MinValueValidator, MaxValueValidator


class GeoLocation(models.Model):
    geolocation_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='geolocations')
    
    # Alternative: Use PostGIS if available
    # location = gis_models.PointField(null=True, blank=True)
    
    # Coordinates for flexibility
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    
    accuracy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        app_label = 'geolocation'
        db_table = 'geolocations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.name} at ({self.latitude}, {self.longitude})"
