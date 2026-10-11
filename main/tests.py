from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse


class PublicPageTests(TestCase):
    fixtures = ['test_catalog']

    def test_public_pages_render(self):
        for name in ('home', 'about', 'help', 'privacy_policy', 'glossary',
                     'collaborators', 'affiliations', 'documentation', 'static_sitemap'):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_home_shows_only_live_announcements(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Catalog Announcement')
        self.assertNotContains(response, 'Deleted Announcement')

    def test_announcements_page_requires_login(self):
        url = reverse('all_announcements')
        self.assertEqual(self.client.get(url).status_code, 302)

        user = get_user_model().objects.create_user(email='reader@example.com', password='pw-12345678')
        self.client.force_login(user)
        self.assertContains(self.client.get(url), 'Test Catalog Announcement')


class SearchCatalogApiTests(TestCase):
    fixtures = ['test_catalog']

    def setUp(self):
        cache.clear()  # the endpoint is cached for a day

    def test_catalog_lists_public_tools_and_resources(self):
        response = self.client.get(reverse('search_catalog'))
        self.assertEqual(response.status_code, 200)
        names = {entry['name'] for entry in response.json()}
        self.assertTrue({'ResFinder', 'AMRFinderPlus', 'GLASS Report'} <= names)
        self.assertNotIn('Pending Example Tool', names)
        self.assertNotIn('Retired Example Tool', names)
