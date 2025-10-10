from django.db import models
from django.utils import timezone

# Create your models here.

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'users'

    def __str__(self):
        return self.name

class User(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('OnLeave', 'On Leave'),
        ('Suspended', 'Suspended'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        app_label = 'users'

    def __str__(self):
        return self.name

class SupervisorAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervisor_assignments')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='officer_assignments')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'users'
        unique_together = ('supervisor', 'officer', 'end_date')

    def __str__(self):
        return f"{self.supervisor} -> {self.officer}"
