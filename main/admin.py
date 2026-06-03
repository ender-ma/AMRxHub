from django.contrib import admin
from django.utils.html import format_html
from .models import Advertisement, Announcement, TeamMember

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_image', 'start_date', 'end_date', 'display_duration', 'is_active')
    list_filter = ('start_date', 'end_date')
    readonly_fields = ['image_preview']
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image Preview'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" height="auto" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Current Image'

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_deleted')
    list_filter = ('is_deleted',)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'display_photo')
    readonly_fields = ['photo_preview']
    
    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" />', obj.photo.url)
        return "No Photo"
    display_photo.short_description = 'Photo'
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="300" height="auto" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = 'Current Photo'
