from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from .models import History

class HistoryListView(LoginRequiredMixin, ListView):
    model = History
    template_name = 'history/history.html'
    context_object_name = 'history_items'

    def get_queryset(self):
        return History.objects.filter(user=self.request.user)

class HistoryDeleteView(LoginRequiredMixin, DeleteView):
    model = History
    success_url = reverse_lazy('history:history')
    template_name = 'history/history_confirm_delete.html'