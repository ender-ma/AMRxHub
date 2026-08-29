from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.resources_list, name='resources_list'),
    path('category/<int:pk>/', views.category_resources, name='category_resources'),
    # path('item/<int:pk>/', views.resource_detail, name='resource_detail'),
    # path('search/', views.search_resources, name='search_resources'),
]