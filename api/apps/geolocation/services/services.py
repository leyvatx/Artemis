from ..repositories.repositories import GeoLocationRepository


class GeoLocationService:
    @staticmethod
    def track_user_location(user, location):
        return GeoLocationRepository.create_geolocation(user, location)

    @staticmethod
    def get_user_location_history(user):
        return GeoLocationRepository.get_geolocations_by_user(user)

    @staticmethod
    def get_latest_location(user):
        latest = GeoLocationRepository.get_geolocations_by_user(user).first()
        return latest.location if latest else None