from django.db import models
from django.utils import timezone

# Create your models here.

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.role_name

class User(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('OnLeave', 'On Leave'),
        ('Suspended', 'Suspended'),
    ]
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField(max_length=150, unique=True)
    user_password_hash = models.CharField(max_length=255)
    user_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user_name

class SupervisorAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervisor_assignments')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='officer_assignments')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('supervisor', 'officer', 'end_date')

    def __str__(self):
        return f"{self.supervisor} -> {self.officer}"
