"""
Utility functions for logging events across the application.
This module provides helpers to create events from different app contexts.
"""

from django.utils import timezone
from apps.users.models import User as UserModel
from .models import Event


class EventLogger:
    """Centralized event logging utility."""
    
    # Biometric Events
    BIOMETRIC_CAPTURE_SUCCESS = 'Biometric_Capture_Success'
    BIOMETRIC_CAPTURE_FAILED = 'Biometric_Capture_Failed'
    FINGERPRINT_REGISTERED = 'Fingerprint_Registered'
    FACE_VERIFIED = 'Face_Verified'
    IRIS_VERIFIED = 'Iris_Verified'
    BIOMETRIC_DATA_DELETED = 'Biometric_Data_Deleted'
    BIOMETRIC_MATCH_FOUND = 'Biometric_Match_Found'
    BIOMETRIC_MATCH_NOT_FOUND = 'Biometric_Match_Not_Found'
    
    # Geolocation Events
    LOCATION_CHANGED = 'Location_Changed'
    GEOFENCE_VIOLATED = 'Geofence_Violated'
    SUSPICIOUS_LOCATION_ACCESS = 'Suspicious_Location_Access'
    LOCATION_TRACKED = 'Location_Tracked'
    
    # Recommendation Events
    RECOMMENDATION_GENERATED = 'Recommendation_Generated'
    RECOMMENDATION_ACCEPTED = 'Recommendation_Accepted'
    RECOMMENDATION_REJECTED = 'Recommendation_Rejected'
    
    # Authentication Events
    LOGIN = 'Login'
    LOGOUT = 'Logout'
    LOGIN_FAILED = 'Login_Failed'
    PASSWORD_CHANGED = 'Password_Changed'
    PASSWORD_RESET = 'Password_Reset'
    SESSION_EXPIRED = 'Session_Expired'
    ACCESS_DENIED = 'Access_Denied'
    
    # Alert and Report Events
    ALERT = 'Alert'
    REPORT = 'Report'
    ALERT_TRIGGERED = 'Alert_Triggered'
    ALERT_RESOLVED = 'Alert_Resolved'
    
    # User Management Events
    USER_CREATED = 'User_Created'
    USER_DELETED = 'User_Deleted'
    USER_MODIFIED = 'User_Modified'
    ROLE_CHANGED = 'Role_Changed'
    
    # Configuration Events
    CONFIGURATION_CHANGED = 'Configuration_Changed'
    ADMIN_ACCESS = 'Admin_Access'
    
    # Data Events
    DATA_EXPORTED = 'Data_Exported'
    DATA_IMPORTED = 'Data_Imported'
    DATA_DELETED = 'Data_Deleted'
    
    # System Events
    SYSTEM = 'System'
    SYSTEM_ERROR = 'System_Error'
    SYSTEM_WARNING = 'System_Warning'
    
    OTHER = 'Other'
    
    @staticmethod
    def log_event(user, title, category, description='', ip_address=None, user_agent=None):
        """
        Create and log an event.
        
        Args:
            user: User instance who triggered the event
            title: Short title for the event
            category: Event category (use EventLogger constants)
            description: Detailed description (optional)
            ip_address: IP address of the request (optional)
            user_agent: User agent string (optional)
            
        Returns:
            Event instance
        """
        # Resolve user: accept a User instance, a user id (int/str), or an anonymous/None.
        resolved_user = None
        try:
            # If user is a Django User instance
            if isinstance(user, UserModel):
                resolved_user = user
            # AnonymousUser or falsy -> keep None
            elif getattr(user, 'is_authenticated', False) is False:
                resolved_user = None
            else:
                # If a numeric id was passed, try to fetch the user
                if isinstance(user, (int, str)):
                    try:
                        resolved_user = UserModel.objects.get(pk=int(user))
                    except Exception:
                        resolved_user = None
                else:
                    resolved_user = None
        except Exception:
            resolved_user = None

        event = Event.objects.create(
            user=resolved_user,
            title=title,
            category=category,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return event
    
    @staticmethod
    def log_biometric_success(user, biometric_type, description='', **kwargs):
        """Log successful biometric capture."""
        title = f"{biometric_type.title()} Captured Successfully"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.BIOMETRIC_CAPTURE_SUCCESS,
            description=f"Biometric type: {biometric_type}. {description}",
            **kwargs
        )
    
    @staticmethod
    def log_biometric_failed(user, biometric_type, reason='', **kwargs):
        """Log failed biometric capture."""
        title = f"{biometric_type.title()} Capture Failed"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.BIOMETRIC_CAPTURE_FAILED,
            description=f"Biometric type: {biometric_type}. Reason: {reason}",
            **kwargs
        )
    
    @staticmethod
    def log_fingerprint_registered(user, finger_name='', **kwargs):
        """Log fingerprint registration."""
        title = f"Fingerprint Registered - {finger_name}" if finger_name else "Fingerprint Registered"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.FINGERPRINT_REGISTERED,
            description=f"Finger: {finger_name}",
            **kwargs
        )
    
    @staticmethod
    def log_face_verified(user, confidence=None, **kwargs):
        """Log face verification."""
        title = "Face Verified"
        description = f"Confidence: {confidence}%" if confidence else ""
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.FACE_VERIFIED,
            description=description,
            **kwargs
        )
    
    @staticmethod
    def log_iris_verified(user, confidence=None, **kwargs):
        """Log iris verification."""
        title = "Iris Verified"
        description = f"Confidence: {confidence}%" if confidence else ""
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.IRIS_VERIFIED,
            description=description,
            **kwargs
        )
    
    @staticmethod
    def log_biometric_deleted(user, biometric_type, **kwargs):
        """Log biometric data deletion."""
        title = f"{biometric_type.title()} Data Deleted"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.BIOMETRIC_DATA_DELETED,
            description=f"Biometric type deleted: {biometric_type}",
            **kwargs
        )
    
    @staticmethod
    def log_location_changed(user, old_location, new_location, **kwargs):
        """Log location change."""
        title = "Location Changed"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.LOCATION_CHANGED,
            description=f"From: {old_location} -> To: {new_location}",
            **kwargs
        )
    
    @staticmethod
    def log_geofence_violated(user, geofence_name, **kwargs):
        """Log geofence violation."""
        title = f"Geofence Violated - {geofence_name}"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.GEOFENCE_VIOLATED,
            description=f"Geofence: {geofence_name}",
            **kwargs
        )
    
    @staticmethod
    def log_suspicious_location(user, location, reason='', **kwargs):
        """Log suspicious location access."""
        title = "Suspicious Location Access"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.SUSPICIOUS_LOCATION_ACCESS,
            description=f"Location: {location}. Reason: {reason}",
            **kwargs
        )
    
    @staticmethod
    def log_recommendation_generated(user, recommendation_id, recommendation_type='', **kwargs):
        """Log recommendation generation."""
        title = f"Recommendation Generated - {recommendation_type}"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.RECOMMENDATION_GENERATED,
            description=f"Recommendation ID: {recommendation_id}",
            **kwargs
        )
    
    @staticmethod
    def log_recommendation_accepted(user, recommendation_id, **kwargs):
        """Log recommendation acceptance."""
        title = "Recommendation Accepted"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.RECOMMENDATION_ACCEPTED,
            description=f"Recommendation ID: {recommendation_id}",
            **kwargs
        )
    
    @staticmethod
    def log_recommendation_rejected(user, recommendation_id, reason='', **kwargs):
        """Log recommendation rejection."""
        title = "Recommendation Rejected"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.RECOMMENDATION_REJECTED,
            description=f"Recommendation ID: {recommendation_id}. Reason: {reason}",
            **kwargs
        )
    
    @staticmethod
    def log_login(user, ip_address=None, user_agent=None):
        """Log user login."""
        return EventLogger.log_event(
            user=user,
            title="User Login",
            category=EventLogger.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_logout(user, ip_address=None, user_agent=None):
        """Log user logout."""
        return EventLogger.log_event(
            user=user,
            title="User Logout",
            category=EventLogger.LOGOUT,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_login_failed(user, reason='', ip_address=None, user_agent=None):
        """Log failed login attempt."""
        return EventLogger.log_event(
            user=user,
            title="Login Failed",
            category=EventLogger.LOGIN_FAILED,
            description=f"Reason: {reason}",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_alert_triggered(user, alert_name, severity='', **kwargs):
        """Log alert trigger."""
        title = f"Alert Triggered - {alert_name}"
        return EventLogger.log_event(
            user=user,
            title=title,
            category=EventLogger.ALERT_TRIGGERED,
            description=f"Severity: {severity}",
            **kwargs
        )
