from ..repositories.repositories import EventRepository


class EventService:
    @staticmethod
    def log_event(user, title, description='', category=''):
        return EventRepository.create_event(user, title, description, category)

    @staticmethod
    def get_user_events(user):
        return EventRepository.get_events_by_user(user)

    @staticmethod
    def get_events_by_category(category):
        return Event.objects.filter(category=category).order_by('-created_at')