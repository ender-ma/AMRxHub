from django.urls import path
from . import views

app_name = 'socials'

urlpatterns = [
    path('', views.social_hub, name='social_hub'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('group/join/<int:group_id>/', views.join_group, name='join_group'),
    path('group/leave/<int:group_id>/', views.leave_group, name='leave_group'),
]