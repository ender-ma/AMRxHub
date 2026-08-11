from admin_portal import fetcher


def test_fetcher_has_fetch_url():
    assert hasattr(fetcher, 'fetch_url')
    assert callable(fetcher.fetch_url)
    # Ensure defaults are integers
    assert isinstance(fetcher.DEFAULT_TIMEOUT, int)
    assert isinstance(fetcher.DEFAULT_RETRIES, int)
