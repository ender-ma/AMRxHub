from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Advertisement, Announcement
from django.utils import timezone
from .models import TeamMember, GlossaryCategory, GlossaryTerm
from django.db.models import Prefetch, Q
from django.shortcuts import redirect
from django.http import FileResponse, Http404, JsonResponse
import os

def home_view(request):
    now = timezone.now()
    adverts = Advertisement.objects.filter(start_date__lte=now, end_date__gte=now)
    announcements = Announcement.objects.filter(is_deleted=False).order_by('-date')[:5]
    return render(request, 'main/home.html', {
        'adverts': adverts,
        'announcements': announcements,
    })

@login_required
def all_announcements(request):
    announcements = Announcement.objects.filter(is_deleted=False).order_by('-date')
    return render(request, 'main/all_announcements.html', {'announcements': announcements})

def about(request):
    team_members = TeamMember.objects.all()
    return render(request, 'main/about.html', {'team_members': team_members}) 
 
def help(request):  
    """
    Render the help page for authenticated users.
    """
    return render(request, 'main/help.html')

def privacy_policy(request):
    """
    Render the privacy policy page for authenticated users.
    """
    return render(request, 'main/privacy_policy.html')

def glossary(request):
    """
    Render the glossary. Only approved, active terms in active categories are shown;
    terms are managed by admins/staff in the Django admin (Main > Glossary terms).
    """
    published = Q(approval_status='approved', is_active=True, category__is_active=True)
    terms = (
        GlossaryTerm.objects.filter(published)
        .select_related('category')
        .prefetch_related(Prefetch('related_terms', queryset=GlossaryTerm.objects.filter(published).only('slug')))
        .order_by('term')
    )
    term_data = [
        {
            'id': t.slug,
            'term': t.term,
            'abbreviation': t.abbreviation,
            'category': t.category.slug,
            'definition': t.definition,
            'context': t.context,
            'references': t.get_references_list(),
            'related': [r.slug for r in t.related_terms.all()],
        }
        for t in terms
    ]
    used = {t['category'] for t in term_data}
    category_data = [
        {'id': c.slug, 'name': c.name, 'icon': c.icon, 'description': c.description}
        for c in GlossaryCategory.objects.filter(is_active=True)
        if c.slug in used
    ]
    return render(request, 'main/glossary.html', {
        'glossary_data': {'categories': category_data, 'terms': term_data},
    })

def collaborators(request):
    """
    Render the collaborators page for authenticated users.
    """
    return render(request, 'main/collaborators.html')


def affiliations(request):
    """
    Render the affiliations page for authenticated users.
    """
    return render(request, 'main/affiliations.html')

def documentation(request):
    """
    Render the documentation page for authenticated users.
    """
    documents = [
        {
            'title': 'AMRx Hub Taxonomy System Hierarchy v0.5.0',
            'file': 'documents/AMRx_Hub_Taxonomy_System_Hierarchy_v0.5.0.docx',
        },
        {
            'title': 'AMRx Hub Admin Staff System v0.5.0',
            'file': 'documents/AMRx_Hub_Admin_Staff_System_v0.5.0.docx',
        },
    ]
    return render(request, 'main/documentation.html', {'documents': documents})

def sitemap_view(request):
    sitemap_path = os.path.join(os.path.dirname(__file__), '..', 'sitemap.xml')
    sitemap_path = os.path.abspath(sitemap_path)
    if not os.path.exists(sitemap_path):
        raise Http404("Sitemap not found.")
    return FileResponse(open(sitemap_path, 'rb'), content_type='application/xml')