from django import forms
from .models import Notification, UserNotificationPreference

class BroadcastNotificationForm(forms.ModelForm):
    """Form for admin to broadcast notifications."""
    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type', 'priority', 'expires_at']
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class NotificationPreferenceForm(forms.ModelForm):
    """Form for users to update notification preferences."""
    class Meta:
        model = UserNotificationPreference
        fields = ['receive_admin_notifications', 'email_notifications']
        labels = {
            'receive_admin_notifications': 'Receive announcements and updates',
            'email_notifications': 'Receive email notifications (in addition to in-app)',
        }