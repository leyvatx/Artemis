from django.db import models

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
        ('Mensual', 'Mensual'),
        ('Incidente', 'Incidente'),
    ]
    
    STATUS_CHOICES = [
        ('Borrador', 'Borrador'),
        ('Generado', 'Generado'),
        ('Archivado', 'Archivado'),
    ]
    
    report_id = models.AutoField(primary_key=True)
    officer = models.ForeignKey(
        'users.User', null=True,
        on_delete=models.SET_NULL,
        related_name='officer_reports',
        db_column='officer_id'
    )
    supervisor = models.ForeignKey(
        'users.User', null=True,  
        on_delete=models.CASCADE,
        related_name='supervisor_reports',
        db_column='supervisor_id'
    )
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Borrador', db_index=True)
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
            models.Index(fields=['officer', 'created_at']),
            models.Index(fields=['report_type', 'status']),
        ]

    def __str__(self):
        return f"{self.report_type} - {self.officer.name} ({self.status})"