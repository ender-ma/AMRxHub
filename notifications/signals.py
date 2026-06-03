from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone

from .models import Notification, UserNotificationPreference

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences when a new user is created."""
    if created:
        UserNotificationPreference.objects.create(user=instance)
        
        # Create welcome notification
        Notification.objects.create(
            user=instance,
            title="Welcome to AMRx Hub!",
            message="Thank you for joining our platform. Explore our tools and resources to enhance your antimicrobial resistance research.",
            notification_type='admin',
            priority='medium',
            is_automated=True
        )

@receiver(user_logged_in)
def user_logged_in_notification(sender, request, user, **kwargs):
    """Create login notification when user logs in."""
    Notification.objects.create(
        user=user,
        title="New Login Detected",
        message=f"You logged in to AMRx Hub at {timezone.now().strftime('%Y-%m-%d %H:%M')}.",
        notification_type='login',
        priority='low',
        is_automated=True
    )