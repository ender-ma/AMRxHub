from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.db import transaction, connection
from .models import CustomUser, LoginAttempt

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_email_verified']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_email_verified']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'is_email_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    actions = ['delete_user_with_profile']
    
    def delete_user_with_profile(self, request, queryset):
        """Admin action to delete users and their profiles"""
        if not request.user.is_staff:
            self.message_user(request, "Only staff can delete user accounts.", level=messages.ERROR)
            return
        
        deleted_count = 0
        for user in queryset:
            try:
                with transaction.atomic():
                    # Log the deletion
                    self.log_deletion(request, user, f"User {user.email} deleted by admin {request.user.email}")
                    user_email = user.email
                    user_id = user.id
                    user.delete()
                    deleted_count += 1
                    
                    self.message_user(
                        request,
                        f"Successfully deleted user: {user_email}",
                        level=messages.SUCCESS
                    )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error deleting user {user.email}: {str(e)}",
                    level=messages.ERROR
                )
        
        if deleted_count > 0:
            self.message_user(
                request,
                f"Successfully deleted {deleted_count} user(s) with their related data.",
                level=messages.SUCCESS
            )
    
    delete_user_with_profile.short_description = "Delete selected users permanently"

class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'timestamp', 'success', 'ip_address']
    list_filter = ['success', 'timestamp']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['user', 'timestamp', 'success', 'ip_address']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(LoginAttempt, LoginAttemptAdmin)