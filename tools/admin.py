from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils import timezone
from .models import ToolCategory, Tool, ToolClick
from .tracking import click_statistics, period_starts

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
    list_display = ['name', 'category', 'tool_type', 'get_approval_status_display', 'institution', 'clicks_7d', 'clicks_30d', 'click_count', 'is_featured', 'is_active', 'created_at']
    list_filter = ['approval_status', 'category', 'tool_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'institution', 'author']
    ordering = ['-created_at']
    list_editable = ['is_featured', 'is_active']
    readonly_fields = ['added_by', 'created_at', 'updated_by', 'updated_at', 'approved_by', 'approved_at', 'click_count']
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'short_description', 'description', 'category')}),
        ('Tool Access', {'fields': ('url', 'tool_type')}),
        ('Additional Information', {'fields': ('institution', 'author', 'version', 'license'), 'classes': ('collapse',)}),
        ('Media', {'fields': ('logo', 'screenshot'), 'classes': ('collapse',)}),
        ('Features & Requirements', {'fields': ('features', 'requirements'), 'classes': ('collapse',)}),
        ('Management', {'fields': ('approval_status', 'rejection_reason', 'is_featured', 'is_active'), 'classes': ('collapse',)}),
        ('Audit', {'fields': ('added_by', 'created_at', 'updated_by', 'updated_at', 'approved_by', 'approved_at', 'click_count')}),
    )
    actions = ['approve_tools', 'reject_tools', 'feature_tools', 'unfeature_tools']

    def get_approval_status_display(self, obj):
        colors = {'pending': '#ff9800', 'approved': '#4caf50', 'rejected': '#f44336'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.approval_status, '#666'), obj.get_approval_status_display())
    get_approval_status_display.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.added_by = request.user
        obj.updated_by = request.user
        if obj.approval_status == 'approved':
            if not obj.approved_by_id or 'approval_status' in form.changed_data:
                obj.approved_by = request.user
                obj.approved_at = timezone.now()
        else:
            obj.approved_by = None
            obj.approved_at = None
        super().save_model(request, obj, form, change)

    def approve_tools(self, request, queryset):
        updated = queryset.update(approval_status='approved', approved_by=request.user, approved_at=timezone.now(), updated_by=request.user)
        self.message_user(request, f'{updated} tools approved successfully.')
    approve_tools.short_description = 'Approve selected tools'

    def reject_tools(self, request, queryset):
        updated = queryset.update(approval_status='rejected', approved_by=None, approved_at=None, updated_by=request.user)
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

    def get_queryset(self, request):
        starts = period_starts()
        return super().get_queryset(request).annotate(
            clicks_7d=Count('clicks', filter=Q(clicks__timestamp__gte=starts['week']), distinct=True),
            clicks_30d=Count('clicks', filter=Q(clicks__timestamp__gte=starts['month']), distinct=True),
        )

    @admin.display(description='Clicks (7d)', ordering='clicks_7d')
    def clicks_7d(self, obj):
        return obj.clicks_7d

    @admin.display(description='Clicks (30d)', ordering='clicks_30d')
    def clicks_30d(self, obj):
        return obj.clicks_30d


@admin.register(ToolClick)
class ToolClickAdmin(admin.ModelAdmin):
    change_list_template = 'admin/tools/toolclick/change_list.html'
    list_display = ['tool', 'tool_category', 'timestamp']
    list_filter = ['timestamp', 'tool__category']
    search_fields = ['tool__name']
    date_hierarchy = 'timestamp'
    list_select_related = ['tool__category']
    fields = ['tool', 'timestamp']
    readonly_fields = ['tool', 'timestamp']

    @admin.display(description='Category', ordering='tool__category__name')
    def tool_category(self, obj):
        return obj.tool.category

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), 'stats': click_statistics()}
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False