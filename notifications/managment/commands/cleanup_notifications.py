from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Cleans up old notifications according to retention policy'

    def handle(self, *args, **options):
        # Get dates for comparison
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        
        # Delete read notifications older than 30 days
        read_deleted = Notification.objects.filter(
            is_read=True,
            read_at__lt=thirty_days_ago
        ).exclude(
            priority='critical'
        ).delete()
        
        # Delete unread notifications older than 60 days, except critical ones
        unread_deleted = Notification.objects.filter(
            is_read=False,
            created_at__lt=sixty_days_ago
        ).exclude(
            priority='critical'
        ).delete()
        
        # Delete expired notifications
        expired_deleted = Notification.objects.filter(
            expires_at__isnull=False,
            expires_at__lt=timezone.now()
        ).delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {read_deleted[0]} read notifications older than 30 days'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {unread_deleted[0]} unread notifications older than 60 days'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {expired_deleted[0]} expired notifications'
        ))