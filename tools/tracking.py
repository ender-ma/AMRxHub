"""Anonymous tool-click tracking and the statistics built on it."""
import hashlib
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Tool, ToolClick

# Repeat clicks on the same tool by the same visitor within this window count once
DEDUPE_SECONDS = 10 * 60

BOT_MARKERS = (
    'bot', 'crawl', 'spider', 'slurp', 'preview', 'facebookexternalhit',
    'curl', 'wget', 'python-requests', 'httpclient', 'headless',
)


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _visitor_hash(request):
    """Hash of IP + browser + today's date. It changes daily, so a visitor
    cannot be followed across days and the raw IP is never stored."""
    raw = '|'.join([
        settings.SECRET_KEY,
        timezone.localdate().isoformat(),
        _client_ip(request),
        request.META.get('HTTP_USER_AGENT', ''),
    ])
    return hashlib.sha256(raw.encode()).hexdigest()


def _is_bot(request):
    agent = request.META.get('HTTP_USER_AGENT', '').lower()
    return not agent or any(marker in agent for marker in BOT_MARKERS)


def record_tool_click(request, tool):
    """Record an anonymous click. Returns True if it was counted."""
    if _is_bot(request):
        return False
    visitor = _visitor_hash(request)
    if not cache.add(f'tool-click:{tool.pk}:{visitor}', True, timeout=DEDUPE_SECONDS):
        return False
    ToolClick.objects.create(tool=tool, visitor_hash=visitor)
    Tool.objects.filter(pk=tool.pk).update(click_count=F('click_count') + 1)
    return True


def period_starts():
    """Start of today, the last 7 days and the last 30 days (local time)."""
    now = timezone.localtime()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        'today': today,
        'week': today - timedelta(days=6),
        'month': today - timedelta(days=29),
    }


def click_statistics(top_n=10):
    starts = period_starts()
    clicks = ToolClick.objects.all()

    periods = []
    for key, label in (('today', 'Today'), ('week', 'Last 7 days'), ('month', 'Last 30 days')):
        in_period = clicks.filter(timestamp__gte=starts[key])
        top_tools = (
            in_period.values('tool__id', 'tool__name', 'tool__category__name')
            .annotate(total=Count('id'))
            .order_by('-total', 'tool__name')[:top_n]
        )
        periods.append({
            'label': label,
            'clicks': in_period.count(),
            'visitors': in_period.exclude(visitor_hash='').values('visitor_hash').distinct().count(),
            'top_tools': list(top_tools),
        })

    daily = {
        row['day']: row['total']
        for row in clicks.filter(timestamp__gte=starts['month'])
        .annotate(day=TruncDate('timestamp'))
        .values('day')
        .annotate(total=Count('id'))
    }
    first_day = starts['month'].date()
    trend = [
        {'day': first_day + timedelta(days=i), 'total': daily.get(first_day + timedelta(days=i), 0)}
        for i in range(30)
    ]
    peak = max((d['total'] for d in trend), default=0) or 1
    for d in trend:
        d['percent'] = round(d['total'] * 100 / peak)

    categories = (
        clicks.filter(timestamp__gte=starts['month'])
        .values('tool__category__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    unused = (
        Tool.objects.filter(is_active=True, approval_status='approved')
        .annotate(recent=Count('clicks', filter=Q(clicks__timestamp__gte=starts['month'])))
        .filter(recent=0)
        .order_by('name')
        .values('id', 'name')
    )

    return {
        'periods': periods,
        'trend': trend,
        'trend_peak': peak,
        'categories': list(categories),
        'unused_tools': list(unused),
        'all_time': clicks.count(),
    }
