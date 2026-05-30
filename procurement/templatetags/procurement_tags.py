from django import template
from django.utils import timezone
import datetime

register = template.Library()


@register.filter
def currency_php(value):
    """Format a decimal as Philippine Peso with commas."""
    try:
        value = float(value)
        return f"₱{value:,.2f}"
    except (TypeError, ValueError):
        return value


@register.filter
def currency_usd(value):
    """Format as USD."""
    try:
        value = float(value)
        return f"${value:,.2f}"
    except (TypeError, ValueError):
        return value


@register.simple_tag
def countdown(dt):
    """Return human-readable countdown to a datetime."""
    now = timezone.now()
    if dt <= now:
        return "Expired"
    delta = dt - now
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


@register.filter
def bid_count(procurement):
    """Return bid count only if past reveal date."""
    if not procurement.is_blind():
        return procurement.bids.filter(status='SUBMITTED').count()
    return '–'
