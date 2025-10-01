from django.core.exceptions import ValidationError
from ..repositories.repositories import MetricTypeRepository, BiometricRepository


class BiometricService:
    @staticmethod
    def record_biometric_data(user, metric_type_name, metric_value):
        metric_type = MetricTypeRepository.get_all_metric_types().filter(type_name=metric_type_name).first()
        if not metric_type:
            raise ValidationError("Metric type not found")
        return BiometricRepository.create_biometric(user, metric_type, metric_value)

    @staticmethod
    def get_user_biometric_history(user):
        return BiometricRepository.get_biometrics_by_user(user)

    @staticmethod
    def get_latest_biometric_value(user, metric_type_name):
        metric_type = MetricTypeRepository.get_all_metric_types().filter(type_name=metric_type_name).first()
        if metric_type:
            latest = BiometricRepository.get_biometrics_by_user(user).filter(metric_type=metric_type).first()
            return latest.metric_value if latest else None
        return None


class MetricTypeService:
    @staticmethod
    def create_metric_type(type_name, unit=''):
        if MetricTypeRepository.get_all_metric_types().filter(type_name=type_name).exists():
            raise ValidationError("Metric type with this name already exists")
        return MetricTypeRepository.create_metric_type(type_name, unit)