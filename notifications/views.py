from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Notification, UserNotificationPreference
from .forms import BroadcastNotificationForm, NotificationPreferenceForm

class NotificationListView(LoginRequiredMixin, ListView):
    """View to list all notifications for a user."""
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 10
    
    def get_queryset(self):
        """Return notifications for current user and universal notifications."""
        return Notification.objects.filter(
            Q(user=self.request.user) | 
            Q(is_universal=True)
        ).order_by('-created_at')
    
    def get_template_names(self):
        """Return different template based on format parameter."""
        if self.request.GET.get('format') == 'html':
            return ['notifications/dropdown.html']
        return [self.template_name]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('format') == 'html':
            # For dropdown, get limited number of notifications
            limit = int(self.request.GET.get('limit', 5))
            context['notifications'] = self.get_queryset()[:limit]
            context['show_all_link'] = True
        return context

class NotificationCountView(LoginRequiredMixin, View):
    """API view to get unread notification count."""
    def get(self, request, *args, **kwargs):
        count = Notification.objects.filter(
            Q(user=request.user) | Q(is_universal=True),
            is_read=False
        ).count()
        return JsonResponse({'count': count})

class MarkNotificationReadView(LoginRequiredMixin, View):
    """View to mark a notification as read."""
    def post(self, request, pk, *args, **kwargs):
        notification = get_object_or_404(
            Notification, 
            Q(user=request.user) | Q(is_universal=True),
            pk=pk
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    
    def get(self, request, pk, *args, **kwargs):
        # Allow GET for simple links
        notification = get_object_or_404(
            Notification, 
            Q(user=request.user) | Q(is_universal=True),
            pk=pk
        )
        notification.mark_as_read()
        return redirect('notifications:notification-list')

class MarkAllReadView(LoginRequiredMixin, View):
    """View to mark all notifications as read."""
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(
            Q(user=request.user) | Q(is_universal=True),
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return JsonResponse({'success': True})

class UpdateNotificationPreferencesView(LoginRequiredMixin, FormView):
    """View to update notification preferences."""
    template_name = 'notifications/preferences.html'
    form_class = NotificationPreferenceForm
    success_url = '/notifications/preferences/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user.notification_preferences
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Notification preferences updated successfully.")
        return super().form_valid(form)

class AdminBroadcastView(UserPassesTestMixin, FormView):
    """Admin view to broadcast notifications to all users."""
    template_name = 'notifications/admin_broadcast.html'
    form_class = BroadcastNotificationForm
    success_url = '/notifications/admin/broadcast/'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        notification = form.save(commit=False)
        notification.is_universal = True
        notification.save()
        
        user_count = notification.user.count() if notification.user else "all"
        messages.success(
            self.request, 
            f"Notification broadcast to {user_count} users successfully."
        )
        return super().form_valid(form)