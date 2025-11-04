default_app_config = 'events.apps.EventsConfig'

__all__ = ['EventLogger']

def __getattr__(name):
    if name == 'EventLogger':
        from .event_logger import EventLogger
        return EventLogger
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
