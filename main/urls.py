from django.contrib import admin
from django.urls import path, include
from . import views 
from . import api
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import sitemap_view
from django.http import HttpResponse
from django.views.decorators.http import require_GET
import os

@require_GET
def static_sitemap(request):
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap.xml')
    with open(sitemap_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/xml')

# Admin site customization
admin.site.site_header = "AMRx Hub Administration"
admin.site.site_title = "AMRx Hub Admin"
admin.site.index_title = "Welcome to AMRx Hub Administration"

# Disable admin password reset
admin.site.password_change = None
admin.site.password_change_done = None
admin.site.password_reset = None
admin.site.password_reset_done = None
admin.site.password_reset_confirm = None
admin.site.password_reset_complete = None

urlpatterns = [
    path("api/search-catalog/", api.search_catalog, name="search_catalog"),
    path('auth/', include('authentication.urls')),
    path('accounts/', include('allauth.urls')),  # Include Allauth URLs for social authentication
    path('profile/', include('profil.urls')),  # Updated to use profil app
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('history/', include('history.urls', namespace='history')),
    
    path('tools/', include('tools.urls', namespace='tools')),
    path('resources/', include('resources.urls', namespace='resources')),
    path('about/', views.about, name='about'),
    path('help/', views.help, name='help'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('glossary/', views.glossary, name='glossary'),
    path('collaborators/', views.collaborators, name='collaborators'),
    path('affiliations/', views.affiliations, name='affiliations'),

    path('announcements/', views.all_announcements, name='all_announcements'),

    path('sitemap.xml', static_sitemap, name='static_sitemap'),

    path("health/", views.health_check, name="health_check"),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)