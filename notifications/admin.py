from django.contrib import admin
from django.utils import timezone
from .models import Notification, UserNotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'priority', 'user', 'is_universal', 
                    'created_at', 'is_read', 'is_automated')
    list_filter = ('notification_type', 'priority', 'is_read', 'is_universal', 'is_automated')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread', 'make_universal']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'message', 'notification_type', 'priority')
        }),
        ('Recipients', {
            'fields': ('user', 'is_universal')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_automated')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at')
        }),
    )
    
    readonly_fields = ('created_at', 'read_at')
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{updated} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{updated} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def make_universal(self, request, queryset):
        updated = queryset.update(is_universal=True)
        self.message_user(request, f"{updated} notifications made universal.")
    make_universal.short_description = "Make selected notifications universal"

@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'receive_admin_notifications', 'email_notifications')
    list_filter = ('receive_admin_notifications', 'email_notifications')
    search_fields = ('user__username', 'user__email')
