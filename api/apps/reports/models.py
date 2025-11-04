from django.db import models


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Generated', 'Generated'),
        ('Sent', 'Sent'),
        ('Archived', 'Archived'),
    ]
    
    report_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        app_label = 'reports'
        db_table = 'reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['report_type', 'status']),
        ]

    def __str__(self):
        return f"{self.report_type} - {self.user.name} ({self.status})"
