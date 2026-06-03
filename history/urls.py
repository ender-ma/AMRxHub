from django.urls import path
from .views import HistoryListView, HistoryDeleteView

app_name = 'history'

urlpatterns = [
    path('', HistoryListView.as_view(), name='history'),
    path('delete/<int:pk>/', HistoryDeleteView.as_view(), name='delete'),  # <-- this name must match the template
]