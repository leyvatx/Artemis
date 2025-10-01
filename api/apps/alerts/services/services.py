from django.core.exceptions import ValidationError
from ..repositories.repositories import AlertTypeRepository, AlertRepository


class AlertService:
    @staticmethod
    def create_alert(user, alert_type_name, description='', location='', alert_level=None):
        alert_type = AlertTypeRepository.get_all_alert_types().filter(type_name=alert_type_name).first()
        if not alert_type:
            raise ValidationError("Alert type not found")
        return AlertRepository.create_alert(user, alert_type, alert_level, description, location)

    @staticmethod
    def acknowledge_alert(alert_id, acknowledged_by):
        alert = AlertRepository.get_alert_by_id(alert_id)
        if alert and alert.alert_status == 'Pending':
            alert.alert_status = 'Acknowledged'
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = timezone.now()
            alert.save()
            return alert
        return None

    @staticmethod
    def resolve_alert(alert_id, resolution_notes=''):
        alert = AlertRepository.get_alert_by_id(alert_id)
        if alert:
            alert.alert_status = 'Resolved'
            alert.resolution_notes = resolution_notes
            alert.save()
            return alert
        return None

    @staticmethod
    def get_pending_alerts():
        return Alert.objects.filter(alert_status='Pending')


class AlertTypeService:
    @staticmethod
    def create_alert_type(type_name, default_level):
        valid_levels = ['Low', 'Medium', 'High', 'Critical']
        if default_level not in valid_levels:
            raise ValidationError("Invalid default level")
        if AlertTypeRepository.get_all_alert_types().filter(type_name=type_name).exists():
            raise ValidationError("Alert type with this name already exists")
        return AlertTypeRepository.create_alert_type(type_name, default_level)