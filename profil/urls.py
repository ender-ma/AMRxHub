from django.urls import path
from . import views

app_name = 'profil'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('update-personal/', views.update_personal_info, name='update_personal'),  # ← Note this name
    path('update-research/', views.update_research_info, name='update_research'),  # ← Note this name
    path('update-settings/', views.update_account_settings, name='update_settings'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('transfer-account/', views.transfer_account, name='transfer_account'),
]