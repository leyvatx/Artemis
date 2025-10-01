from ..models.models import GeoLocation


class GeoLocationRepository:
    @staticmethod
    def get_all_geolocations():
        return GeoLocation.objects.all()

    @staticmethod
    def get_geolocation_by_id(geolocation_id):
        try:
            return GeoLocation.objects.get(pk=geolocation_id)
        except GeoLocation.DoesNotExist:
            return None

    @staticmethod
    def get_geolocations_by_user(user):
        return GeoLocation.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def create_geolocation(user, location):
        return GeoLocation.objects.create(user=user, location=location)

    @staticmethod
    def update_geolocation(geolocation_id, **kwargs):
        geolocation = GeoLocationRepository.get_geolocation_by_id(geolocation_id)
        if geolocation:
            for key, value in kwargs.items():
                setattr(geolocation, key, value)
            geolocation.save()
            return geolocation
        return None

    @staticmethod
    def delete_geolocation(geolocation_id):
        geolocation = GeoLocationRepository.get_geolocation_by_id(geolocation_id)
        if geolocation:
            geolocation.delete()
            return True
        return False