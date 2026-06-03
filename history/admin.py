from django.contrib import admin
from .models import History

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'viewed_on']
    list_filter = ['content_type', 'viewed_on']
    search_fields = ['user__username']
    readonly_fields = ['user', 'content_type', 'object_id', 'viewed_on']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False