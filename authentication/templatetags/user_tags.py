from django import template

register = template.Library()

@register.filter
def user_display(user):
    """Returns a user's display name."""
    if not user or user.is_anonymous:
        return "Guest"
    
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    elif hasattr(user, 'username') and user.username:
        return user.username
    
    return user.email