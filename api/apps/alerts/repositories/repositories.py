from ..models.models import AlertType, Alert


class AlertTypeRepository:
    @staticmethod
    def get_all_alert_types():
        return AlertType.objects.all()

    @staticmethod
    def get_alert_type_by_id(alert_type_id):
        try:
            return AlertType.objects.get(pk=alert_type_id)
        except AlertType.DoesNotExist:
            return None

    @staticmethod
    def create_alert_type(type_name, default_level):
        return AlertType.objects.create(type_name=type_name, default_level=default_level)

    @staticmethod
    def update_alert_type(alert_type_id, **kwargs):
        alert_type = AlertTypeRepository.get_alert_type_by_id(alert_type_id)
        if alert_type:
            for key, value in kwargs.items():
                setattr(alert_type, key, value)
            alert_type.save()
            return alert_type
        return None

    @staticmethod
    def delete_alert_type(alert_type_id):
        alert_type = AlertTypeRepository.get_alert_type_by_id(alert_type_id)
        if alert_type:
            alert_type.delete()
            return True
        return False


class AlertRepository:
    @staticmethod
    def get_all_alerts():
        return Alert.objects.all()

    @staticmethod
    def get_alert_by_id(alert_id):
        try:
            return Alert.objects.get(pk=alert_id)
        except Alert.DoesNotExist:
            return None

    @staticmethod
    def get_alerts_by_user(user):
        return Alert.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def create_alert(user, alert_type, alert_level=None, description='', location=''):
        if not alert_level:
            alert_level = alert_type.default_level
        return Alert.objects.create(
            user=user,
            alert_type=alert_type,
            alert_level=alert_level,
            description=description,
            location=location
        )

    @staticmethod
    def update_alert(alert_id, **kwargs):
        alert = AlertRepository.get_alert_by_id(alert_id)
        if alert:
            for key, value in kwargs.items():
                setattr(alert, key, value)
            alert.save()
            return alert
        return None

    @staticmethod
    def delete_alert(alert_id):
        alert = AlertRepository.get_alert_by_id(alert_id)
        if alert:
            alert.delete()
            return True
        return False