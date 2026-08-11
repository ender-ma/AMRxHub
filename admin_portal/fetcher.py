"""
Simple HTTP fetcher with retries and configurable timeout for research agent.
Uses requests with urllib3 Retry for robust retries/backoff.
"""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    DEFAULT_TIMEOUT = int(getattr(settings, 'RESEARCH_FETCH_TIMEOUT', 30))
except Exception:
    DEFAULT_TIMEOUT = 30
try:
    DEFAULT_RETRIES = int(getattr(settings, 'RESEARCH_FETCH_RETRIES', 3))
except Exception:
    DEFAULT_RETRIES = 3


def _build_session(retries: int = DEFAULT_RETRIES, backoff_factor: float = 0.5, status_forcelist=(429, 500, 502, 503, 504)) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(['GET', 'POST'])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


def fetch_url(url: str, timeout: int | None = None, session: requests.Session | None = None) -> dict:
    """Fetch a URL with retries.
    Returns dict with keys: status_code, headers, text
    Raises requests.RequestException on failure.
    """
    if not timeout:
        timeout = DEFAULT_TIMEOUT
    if session is None:
        session = _build_session()
    logger.debug('Fetching URL %s with timeout=%s', url, timeout)
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return {'status_code': resp.status_code, 'headers': dict(resp.headers), 'text': resp.text}
