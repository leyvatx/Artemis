from ..models.models import MetricType, Biometric


class MetricTypeRepository:
    @staticmethod
    def get_all_metric_types():
        return MetricType.objects.all()

    @staticmethod
    def get_metric_type_by_id(metric_type_id):
        try:
            return MetricType.objects.get(pk=metric_type_id)
        except MetricType.DoesNotExist:
            return None

    @staticmethod
    def create_metric_type(type_name, unit=''):
        return MetricType.objects.create(type_name=type_name, unit=unit)

    @staticmethod
    def update_metric_type(metric_type_id, **kwargs):
        metric_type = MetricTypeRepository.get_metric_type_by_id(metric_type_id)
        if metric_type:
            for key, value in kwargs.items():
                setattr(metric_type, key, value)
            metric_type.save()
            return metric_type
        return None

    @staticmethod
    def delete_metric_type(metric_type_id):
        metric_type = MetricTypeRepository.get_metric_type_by_id(metric_type_id)
        if metric_type:
            metric_type.delete()
            return True
        return False


class BiometricRepository:
    @staticmethod
    def get_all_biometrics():
        return Biometric.objects.all()

    @staticmethod
    def get_biometric_by_id(biometric_id):
        try:
            return Biometric.objects.get(pk=biometric_id)
        except Biometric.DoesNotExist:
            return None

    @staticmethod
    def get_biometrics_by_user(user):
        return Biometric.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def create_biometric(user, metric_type, metric_value):
        return Biometric.objects.create(
            user=user,
            metric_type=metric_type,
            metric_value=metric_value
        )

    @staticmethod
    def update_biometric(biometric_id, **kwargs):
        biometric = BiometricRepository.get_biometric_by_id(biometric_id)
        if biometric:
            for key, value in kwargs.items():
                setattr(biometric, key, value)
            biometric.save()
            return biometric
        return None

    @staticmethod
    def delete_biometric(biometric_id):
        biometric = BiometricRepository.get_biometric_by_id(biometric_id)
        if biometric:
            biometric.delete()
            return True
        return False