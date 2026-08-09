from django.http import JsonResponse
from . import views as portal_views


def metrics_view(request):
    """Return sanitized metrics for dashboard charts/summary.
    This deliberately avoids serializing complex queryset objects.
    """
    metrics = portal_views._dashboard_metrics()
    payload = {}
    for k, v in metrics.items():
        if k == 'recent_notifications':
            # summarize notifications
            payload[k] = [
                {'id': getattr(n, 'id', None), 'title': getattr(n, 'title', str(n))} for n in v[:8]
            ] if v is not None else []
        else:
            try:
                # basic serializable values (counts, ints, strings)
                int_v = int(v)
                payload[k] = int_v
            except Exception:
                # fallback: string representation
                payload[k] = str(v)
    return JsonResponse({'metrics': payload})