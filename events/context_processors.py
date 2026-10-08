from .models import EventConfig


def event_config(request):
    """Make event config available in all templates."""
    try:
        config = EventConfig.get_config()
        day_range = range(1, config.total_days + 1)
    except Exception:
        config = None
        day_range = range(1, 21)
    return {'event_config': config, 'day_range': day_range}
