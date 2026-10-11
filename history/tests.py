from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import History


class HistoryTests(TestCase):
    fixtures = ['test_catalog']

    def setUp(self):
        self.user = get_user_model().objects.create_user(email='viewer@example.com', password='pw-12345678')

    def test_history_requires_login(self):
        self.assertEqual(self.client.get(reverse('history:history')).status_code, 302)

    def test_viewing_a_tool_is_added_to_history(self):
        self.client.force_login(self.user)
        self.client.get(reverse('tools:tool_detail', args=[9101]))
        self.assertEqual(History.objects.filter(user=self.user).count(), 1)
        self.assertContains(self.client.get(reverse('history:history')), 'ResFinder')
