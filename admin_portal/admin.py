from django.contrib import admin
from .models import AIJob, AIRequestLog, PipelineRun, AIContentSuggestion, AIPreferences


@admin.register(AIJob)
class AIJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'agent_key', 'status', 'created_at', 'created_by')
    list_filter = ('agent_key', 'status')
    search_fields = ('url',)


@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'timestamp', 'model', 'success')
    list_filter = ('model', 'success')


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'status', 'created_at', 'created_by')
    list_filter = ('status',)


@admin.register(AIContentSuggestion)
class AIContentSuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'object_type', 'status', 'confidence_score', 'quality_score', 'created_at')
    list_filter = ('status', 'object_type')
    search_fields = ('title', 'url')
    readonly_fields = ('detailed_metadata', 'provenance')


@admin.register(AIPreferences)
class AIPreferencesAdmin(admin.ModelAdmin):
    list_display = ('id', 'default_model', 'research_model', 'classification_model', 'research_fetch_timeout')
    readonly_fields = ()
    fieldsets = (
        (None, {'fields': ('default_model',)}),
        ('Per-agent models', {'fields': ('research_model', 'classification_model', 'metadata_model', 'quality_model')}),
        ('Fetcher', {'fields': ('research_fetch_timeout', 'research_fetch_retries')}),
    )
    def has_add_permission(self, request):
        # discourage multiple instances; allow only one entry through admin UX
        return not AIPreferences.objects.exists()

    def get_queryset(self, request):
        # ensure admin shows the latest preferences row
        qs = super().get_queryset(request)
        return qs
