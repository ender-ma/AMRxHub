"""
Base CBVs and mixins for admin_portal.
"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return bool(self.request.user and self.request.user.is_active and self.request.user.is_staff)


class AdminBaseView(StaffRequiredMixin, TemplateView):
    """Base admin template view that ensures staff access and provides common context."""
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault('admin_active', True)
        return ctx


class AdminListView(StaffRequiredMixin, ListView):
    paginate_by = 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault('admin_active', True)
        return ctx


class AdminDetailView(StaffRequiredMixin, DetailView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault('admin_active', True)
        return ctx
