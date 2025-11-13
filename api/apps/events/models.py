from django.db import models


class Event(models.Model):
    EVENT_CATEGORIES = [
        # Autenticación
        ('Login', 'Login'),
        ('Logout', 'Logout'),
        ('Login_Failed', 'Login Failed'),
        ('Password_Changed', 'Password Changed'),
        ('Password_Reset', 'Password Reset'),
        ('Session_Expired', 'Session Expired'),
        ('Access_Denied', 'Access Denied'),
        
        # Biometría
        ('Biometric_Capture_Success', 'Biometric Capture Success'),
        ('Biometric_Capture_Failed', 'Biometric Capture Failed'),
        ('Fingerprint_Registered', 'Fingerprint Registered'),
        ('Face_Verified', 'Face Verified'),
        ('Iris_Verified', 'Iris Verified'),
        ('Biometric_Data_Deleted', 'Biometric Data Deleted'),
        ('Biometric_Match_Found', 'Biometric Match Found'),
        ('Biometric_Match_Not_Found', 'Biometric Match Not Found'),
        
        # Geolocalización
        ('Location_Changed', 'Location Changed'),
        ('Geofence_Violated', 'Geofence Violated'),
        ('Suspicious_Location_Access', 'Suspicious Location Access'),
        ('Location_Tracked', 'Location Tracked'),
        
        # Recomendaciones
        ('Recommendation_Generated', 'Recommendation Generated'),
        ('Recommendation_Accepted', 'Recommendation Accepted'),
        ('Recommendation_Rejected', 'Recommendation Rejected'),
        
        # Alertas y Reportes
        ('Alert', 'Alert'),
        ('Report', 'Report'),
        ('Alert_Triggered', 'Alert Triggered'),
        ('Alert_Resolved', 'Alert Resolved'),
        
        # Administración
        ('User_Created', 'User Created'),
        ('User_Deleted', 'User Deleted'),
        ('User_Modified', 'User Modified'),
        ('Role_Changed', 'Role Changed'),
        ('Configuration_Changed', 'Configuration Changed'),
        ('Admin_Access', 'Admin Access'),
        
        # Datos
        ('Data_Exported', 'Data Exported'),
        ('Data_Imported', 'Data Imported'),
        ('Data_Deleted', 'Data Deleted'),
        
        # Sistema
        ('System', 'System'),
        ('System_Error', 'System Error'),
        ('System_Warning', 'System Warning'),
        
        # Otros
        ('Other', 'Other'),
    ]
    
    event_id = models.AutoField(primary_key=True)
    # Allow events without a linked user (e.g. anonymous, system) and keep events
    # if a user is deleted by using SET_NULL.
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=EVENT_CATEGORIES, default='Other', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'events'
        db_table = 'events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['category', 'created_at']),
        ]

    def __str__(self):
        user_part = self.user.name if self.user else 'Anonymous'
        return f"{self.title} - {user_part}"
