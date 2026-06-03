from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('list/', views.NotificationListView.as_view(), name='notification-list'),
    path('count/', views.NotificationCountView.as_view(), name='notification-count'),
    path('mark-read/<uuid:pk>/', views.MarkNotificationReadView.as_view(), name='mark-read'),
    path('preferences/', views.UpdateNotificationPreferencesView.as_view(), name='notification-preferences'),
    path('admin/broadcast/', views.AdminBroadcastView.as_view(), name='admin-broadcast'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark-all-read'),
]