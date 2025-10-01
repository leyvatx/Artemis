from ..models.models import Event


class EventRepository:
    @staticmethod
    def get_all_events():
        return Event.objects.all()

    @staticmethod
    def get_event_by_id(event_id):
        try:
            return Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return None

    @staticmethod
    def get_events_by_user(user):
        return Event.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def create_event(user, title, description='', category=''):
        return Event.objects.create(
            user=user,
            title=title,
            description=description,
            category=category
        )

    @staticmethod
    def update_event(event_id, **kwargs):
        event = EventRepository.get_event_by_id(event_id)
        if event:
            for key, value in kwargs.items():
                setattr(event, key, value)
            event.save()
            return event
        return None

    @staticmethod
    def delete_event(event_id):
        event = EventRepository.get_event_by_id(event_id)
        if event:
            event.delete()
            return True
        return False