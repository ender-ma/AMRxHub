from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.html import format_html
from .models import Advertisement, Announcement, TeamMember, GlossaryCategory, GlossaryTerm

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


# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------

GLOSSARY_AUDIT_FIELDS = ['added_by', 'created_at', 'updated_by', 'updated_at', 'approved_by', 'approved_at']


def stamp_glossary_audit(obj, user, changed_data):
    """Fill audit fields from the admin/staff member who is saving."""
    if not obj.pk:
        obj.added_by = user
    obj.updated_by = user
    if obj.approval_status == 'approved':
        if not obj.approved_by_id or 'approval_status' in changed_data:
            obj.approved_by = user
            obj.approved_at = timezone.now()
    else:
        obj.approved_by = None
        obj.approved_at = None


class GlossaryTermInline(admin.TabularInline):
    model = GlossaryTerm
    extra = 0
    fields = ('term', 'abbreviation', 'approval_status', 'is_active')
    show_change_link = True


@admin.register(GlossaryCategory)
class GlossaryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order', 'published_terms', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [GlossaryTermInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _published=Count('terms', filter=Q(terms__approval_status='approved', terms__is_active=True))
        )

    def published_terms(self, obj):
        return obj._published
    published_terms.short_description = 'Published terms'
    published_terms.admin_order_field = '_published'

    def save_formset(self, request, form, formset, change):
        if formset.model is not GlossaryTerm:
            return super().save_formset(request, form, formset, change)
        changed = {id(f.instance): f.changed_data for f in formset.forms}
        instances = formset.save(commit=False)
        for obj in instances:
            stamp_glossary_audit(obj, request.user, changed.get(id(obj), []))
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ('term', 'abbreviation', 'category', 'status_badge', 'is_active', 'updated_by', 'updated_at')
    list_filter = ('approval_status', 'category', 'is_active')
    search_fields = ('term', 'abbreviation', 'definition', 'context')
    prepopulated_fields = {'slug': ('term',)}
    filter_horizontal = ('related_terms',)
    readonly_fields = GLOSSARY_AUDIT_FIELDS
    actions = ['approve_terms', 'reject_terms']
    fieldsets = (
        (None, {'fields': ('category', 'term', 'slug', 'abbreviation', 'definition')}),
        ('More detail (optional)', {'fields': ('context', 'references', 'related_terms')}),
        ('Management', {'fields': ('approval_status', 'is_active')}),
        ('Audit', {'fields': GLOSSARY_AUDIT_FIELDS, 'classes': ('collapse',)}),
    )

    def status_badge(self, obj):
        colors = {'pending': '#d97706', 'approved': '#16a34a', 'rejected': '#dc2626'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>',
                           colors.get(obj.approval_status, '#666'), obj.get_approval_status_display())
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'approval_status'

    def save_model(self, request, obj, form, change):
        stamp_glossary_audit(obj, request.user, form.changed_data)
        super().save_model(request, obj, form, change)

    @admin.action(description='Approve selected terms')
    def approve_terms(self, request, queryset):
        updated = queryset.update(approval_status='approved', approved_by=request.user,
                                  approved_at=timezone.now(), updated_by=request.user)
        self.message_user(request, f'{updated} term(s) approved.')

    @admin.action(description='Reject selected terms')
    def reject_terms(self, request, queryset):
        updated = queryset.update(approval_status='rejected', approved_by=None,
                                  approved_at=None, updated_by=request.user)
        self.message_user(request, f'{updated} term(s) rejected.')
