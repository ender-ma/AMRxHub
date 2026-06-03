from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ToolCategory, Tool, ToolClick

@admin.register(ToolCategory)
class ToolCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'get_tools_count_display', 'order', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'description', 'order', 'is_active', 'category_type')}),
        ('Appearance', {'fields': ('icon', 'color'), 'description': 'Customize how this category appears to users'}),
    )

    fieldsets = (
        ('Basic Information', {'fields': ('name', 'description', 'detailed_description', 'order', 'is_active', 'category_type')}),
        ('Appearance', {'fields': ('icon', 'color'), 'description': 'Customize how this category appears to users'}),
    )

    def get_tools_count_display(self, obj):
        count = obj.get_tools_count()
        return format_html('<span style="background:#e1f5fe;padding:2px 6px;border-radius:3px;">{}</span>', count)
    get_tools_count_display.short_description = 'Active Tools'

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'tool_type', 'get_approval_status_display', 'institution', 'click_count', 'is_featured', 'is_active', 'created_at']
    list_filter = ['approval_status', 'category', 'tool_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'institution', 'author']
    ordering = ['-created_at']
    list_editable = ['is_featured', 'is_active']
    readonly_fields = ['added_by', 'approved_by', 'approved_at', 'click_count']
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'short_description', 'description', 'category')}),
        ('Tool Access', {'fields': ('url', 'tool_type')}),
        ('Additional Information', {'fields': ('institution', 'author', 'version', 'license'), 'classes': ('collapse',)}),
        ('Media', {'fields': ('logo', 'screenshot'), 'classes': ('collapse',)}),
        ('Features & Requirements', {'fields': ('features', 'requirements'), 'classes': ('collapse',)}),
        ('Management', {'fields': ('approval_status', 'rejection_reason', 'is_featured', 'is_active'), 'classes': ('collapse',)}),
    )
    actions = ['approve_tools', 'reject_tools', 'feature_tools', 'unfeature_tools']

    def get_approval_status_display(self, obj):
        colors = {'pending': '#ff9800', 'approved': '#4caf50', 'rejected': '#f44336'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.approval_status, '#666'), obj.get_approval_status_display())
    get_approval_status_display.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.added_by = request.user
            if request.user.is_staff:
                obj.approval_status = 'approved'
                obj.approved_by = request.user
                obj.approved_at = timezone.now()
        elif obj.approval_status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)

    def approve_tools(self, request, queryset):
        updated = queryset.update(approval_status='approved', approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f'{updated} tools approved successfully.')
    approve_tools.short_description = 'Approve selected tools'

    def reject_tools(self, request, queryset):
        updated = queryset.update(approval_status='rejected')
        self.message_user(request, f'{updated} tools rejected.')
    reject_tools.short_description = 'Reject selected tools'

    def feature_tools(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} tools featured.')
    feature_tools.short_description = 'Feature selected tools'

    def unfeature_tools(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} tools unfeatured.')
    unfeature_tools.short_description = 'Unfeature selected tools'
    
    def total_views(self, obj):
        return History.objects.filter(content_type__model='tool', object_id=obj.id).count()
    total_views.short_description = 'Total Views'

    def unique_users(self, obj):
        return History.objects.filter(content_type__model='tool', object_id=obj.id).values('user').distinct().count()
    unique_users.short_description = 'Unique Users'

@admin.register(ToolClick)
class ToolClickAdmin(admin.ModelAdmin):
    list_display = ['tool', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp', 'tool__category']
    search_fields = ['tool__name', 'user__username', 'ip_address']
    readonly_fields = ['tool', 'user', 'ip_address', 'timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False