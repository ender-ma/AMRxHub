import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    """Model for system notifications sent to users."""
    
    # Notification types
    TYPE_CHOICES = (
        ('system', 'System Message'),
        ('admin', 'Admin Message'),
        ('maintenance', 'Maintenance Alert'),
        ('update', 'Platform Update'),
        ('login', 'Login Alert'),
        ('general', 'General Message'),
    )
    
    # Priority levels
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True, 
        blank=True
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_automated = models.BooleanField(default=False)
    is_universal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['is_universal', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read and set read timestamp."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def is_expired(self):
        """Check if notification has expired."""
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False


class UserNotificationPreference(models.Model):
    """User preferences for notification settings."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    receive_admin_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"