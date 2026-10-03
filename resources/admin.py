from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import ResourceCategory, ResourceItem

AUDIT_FIELDS = ['added_by', 'created_at', 'updated_by', 'updated_at', 'approved_by', 'approved_at']


def stamp_audit(obj, user, changed_data):
    """Fill audit fields from the admin who is saving."""
    if not obj.pk:
        obj.added_by = user
    obj.updated_by = user
    if obj.approval_status == 'approved':
        # Record the approver when it becomes approved (or was never recorded)
        if not obj.approved_by_id or 'approval_status' in changed_data:
            obj.approved_by = user
            obj.approved_at = timezone.now()
    else:
        obj.approved_by = None
        obj.approved_at = None


class ResourceItemInline(admin.TabularInline):
    model = ResourceItem
    extra = 1
    readonly_fields = ['file_preview'] + AUDIT_FIELDS

    def file_preview(self, obj):
        html = ""
        if obj.image:
            html += format_html('<img src="{}" width="100" height="auto" /><br>', obj.image.url)
        if obj.pdf_file:
            html += format_html('<a href="{}" target="_blank">View PDF</a>', obj.pdf_file.url)
        return html or "No files"
    file_preview.short_description = 'Preview'

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    inlines = [ResourceItemInline]
    list_display = ('name', 'description')

    def save_formset(self, request, form, formset, change):
        if formset.model is not ResourceItem:
            return super().save_formset(request, form, formset, change)
        changed = {id(f.instance): f.changed_data for f in formset.forms}
        instances = formset.save(commit=False)
        for obj in instances:
            stamp_audit(obj, request.user, changed.get(id(obj), []))
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()

@admin.register(ResourceItem)
class ResourceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'display_image', 'has_pdf', 'approval_status', 'approved_by', 'updated_by')
    fields = ('category', 'title', 'description', 'link', 'link_text', 'link_icon', 'pdf_file', 'image', 'image_preview', 'pdf_preview', 'approval_status', 'is_active', *AUDIT_FIELDS)
    readonly_fields = ['image_preview', 'pdf_preview'] + AUDIT_FIELDS

    def save_model(self, request, obj, form, change):
        stamp_audit(obj, request.user, form.changed_data)
        super().save_model(request, obj, form, change)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'

    def has_pdf(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.pdf_file.url)
        return "No PDF"
    has_pdf.short_description = 'PDF File'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" height="auto" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank" class="button">View PDF</a>', obj.pdf_file.url)
        return "No PDF file uploaded"
    pdf_preview.short_description = 'PDF Preview'