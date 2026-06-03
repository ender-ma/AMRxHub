from django.contrib import admin
from .models import ChatRoom, ChatMessage, ResearchGroup, FeaturedResearcher

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_private', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_private', 'created_at')
    filter_horizontal = ('allowed_users',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'room', 'timestamp', 'short_content')
    search_fields = ('content', 'author__email')
    list_filter = ('room', 'timestamp')
    readonly_fields = ('timestamp',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_count', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

@admin.register(FeaturedResearcher)
class FeaturedResearcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'is_currently_featured')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('start_date', 'end_date')
    
    def is_currently_featured(self, obj):
        return obj.is_active
    is_currently_featured.boolean = True
    is_currently_featured.short_description = 'Currently Featured'