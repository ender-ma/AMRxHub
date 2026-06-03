from django import template
from django.db.models import Q
from ..models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def get_unread_count(context):
    """Return unread notification count for current user."""
    request = context['request']
    if not request.user.is_authenticated:
        return 0
    
    return Notification.objects.filter(
        Q(user=request.user) | Q(is_universal=True),
        is_read=False
    ).count()

@register.inclusion_tag('notifications/recent_notifications.html', takes_context=True)
def get_recent_notifications(context, count=5):
    """Return N most recent notifications for display."""
    request = context['request']
    if not request.user.is_authenticated:
        return {'notifications': []}
    
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(is_universal=True)
    ).order_by('-created_at')[:count]
    
    return {'notifications': notifications}