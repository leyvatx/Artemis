from .models import *from django.db import models

# Create your models here.

class Recommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    alert = models.ForeignKey('alerts.Alert', on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:50]
