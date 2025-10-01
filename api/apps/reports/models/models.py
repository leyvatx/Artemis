from django.db import models
from apps.users.models import User

# Create your models here.

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'reports'

    def __str__(self):
        return f"{self.report_type} by {self.user}"
