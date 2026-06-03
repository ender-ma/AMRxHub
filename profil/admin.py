from django.contrib import admin
from .models import UserProfile, ResearchInterest
from django import forms
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib import messages

class BulkInterestForm(forms.Form):
    interests = forms.CharField(
        widget=forms.Textarea, 
        help_text="Enter one research interest per line"
    )

@admin.register(ResearchInterest)
class ResearchInterestAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    
    @admin.action(description="Mark selected interests as deprecated")
    def mark_deprecated(self, request, queryset):
        # This example prepends "[Deprecated] " to the name
        for interest in queryset:
            interest.name = f"[Deprecated] {interest.name}"
            interest.save()
    
    actions = [mark_deprecated]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_view), 
                 name='profil_researchinterest_bulk_add'),
        ]
        return custom_urls + urls
    
    def bulk_add_view(self, request):
        if request.method == 'POST':
            form = BulkInterestForm(request.POST)
            if form.is_valid():
                interests = form.cleaned_data['interests'].split('\n')
                count = 0
                for interest in interests:
                    interest = interest.strip()
                    if interest:
                        ResearchInterest.objects.get_or_create(name=interest)
                        count += 1
                messages.success(request, f'Successfully added {count} research interests.')
                return redirect('admin:profil_researchinterest_changelist')
        else:
            form = BulkInterestForm()
        
        context = {
            'form': form,
            'title': 'Bulk Add Research Interests',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/profil/researchinterest/bulk_add.html', context)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'organization', 'country', 'get_interests_count')
    search_fields = ('user__email', 'role', 'organization', 'country')
    list_filter = ('role', 'country', 'interests')
    filter_horizontal = ('interests',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('department', 'role', 'organization', 'country')
        }),
        ('Research Information', {
            'fields': ('interests', 'research_background')
        }),
        ('Account Settings', {
            'fields': ('receive_research_updates', 'receive_email_notifications', 'profile_visibility')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_interests_count(self, obj):
        return obj.interests.count()
    get_interests_count.short_description = 'Research Interests'

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow viewing but prevent editing
        return request.method in ['GET', 'HEAD']
    
    def has_delete_permission(self, request, obj=None):
        return False
