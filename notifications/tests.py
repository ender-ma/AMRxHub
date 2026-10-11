from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class NotificationTests(TestCase):
    def test_count_requires_login(self):
        self.assertEqual(self.client.get(reverse('notifications:notification-count')).status_code, 302)

    def test_count_for_signed_in_user(self):
        user = get_user_model().objects.create_user(email='member@example.com', password='pw-12345678')
        self.client.force_login(user)
        response = self.client.get(reverse('notifications:notification-count'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.json())
