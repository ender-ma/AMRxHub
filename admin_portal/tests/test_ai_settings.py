import unittest
from django.test import SimpleTestCase, override_settings
from admin_portal.ai_settings import get_ai_model


class AIPreferencesTests(SimpleTestCase):
    @override_settings(OPENAI_DEFAULT_MODEL='env-default', RESEARCH_AGENT_MODEL='env-research')
    def test_get_ai_model_uses_settings_fallbacks(self):
        self.assertEqual(get_ai_model('research'), 'env-research')
        self.assertEqual(get_ai_model('classification'), 'env-default')


if __name__ == '__main__':
    unittest.main()
