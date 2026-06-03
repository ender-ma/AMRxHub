from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tools_home, name='tools_home'),
    path('tools/', views.tools, name='tools'),
    path('category/<int:category_id>/', views.category_tools, name='category_tools'),
    path('tool/<int:tool_id>/', views.tool_detail, name='tool_detail'),
    path('tool/<int:tool_id>/redirect/', views.tool_redirect, name='tool_redirect'),
    path('search/', views.search_tools, name='search_tools'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('history/', views.history, name='history'),
    path('ajax/search/', views.ajax_search_tools, name='ajax_search_tools'),
    path('access/<int:tool_id>/', views.tool_access, name='tool_access'),

]