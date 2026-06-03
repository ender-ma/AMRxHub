from django.contrib import admin
from django.utils.html import format_html
from .models import ResourceCategory, ResourceItem

class ResourceItemInline(admin.TabularInline):
    model = ResourceItem
    extra = 1
    readonly_fields = ['file_preview']

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

@admin.register(ResourceItem)
class ResourceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'display_image', 'has_pdf')
    fields = ('category', 'title', 'description', 'link', 'link_text', 'link_icon', 'pdf_file', 'image', 'image_preview', 'pdf_preview')
    readonly_fields = ['image_preview', 'pdf_preview']

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