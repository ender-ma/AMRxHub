import unittest
from admin_portal import fetcher


class FetcherSanityTests(unittest.TestCase):
    def test_fetcher_has_fetch_url(self):
        self.assertTrue(hasattr(fetcher, 'fetch_url'))
        self.assertTrue(callable(fetcher.fetch_url))

    def test_fetcher_defaults(self):
        self.assertIsInstance(fetcher.DEFAULT_TIMEOUT, int)
        self.assertIsInstance(fetcher.DEFAULT_RETRIES, int)


if __name__ == '__main__':
    unittest.main()
