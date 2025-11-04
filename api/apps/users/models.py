from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'users'
        db_table = 'roles'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

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
    email = models.EmailField(max_length=150, unique=True, validators=[EmailValidator()])
    password_hash = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = 'users'
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.email})"


class SupervisorAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    supervisor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='supervisor_assignments',
        limit_choices_to={'status': 'Active'}
    )
    officer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='officer_assignments',
        limit_choices_to={'status': 'Active'}
    )
    start_date = models.DateTimeField(default=timezone.now, db_index=True)
    end_date = models.DateTimeField(null=True, blank=True, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'users'
        db_table = 'supervisor_assignments'
        unique_together = ('supervisor', 'officer', 'end_date')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['supervisor', 'end_date']),
            models.Index(fields=['officer', 'end_date']),
        ]

    def __str__(self):
        return f"{self.supervisor.name} supervises {self.officer.name}"
