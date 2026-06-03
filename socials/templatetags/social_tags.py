from django import template
from django.utils import timezone
from socials.models import FeaturedResearcher

register = template.Library()

@register.simple_tag
def get_featured_researchers():
    """Get currently featured researchers"""
    today = timezone.now().date()
    return FeaturedResearcher.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).select_related('user')