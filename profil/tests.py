from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ProfileTests(TestCase):
    def test_profile_requires_login(self):
        self.assertEqual(self.client.get(reverse('profil:profile')).status_code, 302)

    def test_profile_renders_for_signed_in_user(self):
        user = get_user_model().objects.create_user(email='member@example.com', password='pw-12345678')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('profil:profile')).status_code, 200)
