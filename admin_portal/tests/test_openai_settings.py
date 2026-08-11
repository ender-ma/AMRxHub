import os
import unittest
from django.conf import settings


class OpenAISettingsTests(unittest.TestCase):
    def test_openai_default_model_present_or_env(self):
        val = getattr(settings, 'OPENAI_DEFAULT_MODEL', None)
        env = os.environ.get('OPENAI_DEFAULT_MODEL')
        # Accept if settings provides it or environment variable is set.
        self.assertTrue(val is not None or env is not None)


if __name__ == '__main__':
    unittest.main()
