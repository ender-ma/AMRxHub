from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from main import errors


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


class ErrorPageTests(TestCase):
    def test_unknown_url_shows_custom_404(self):
        response = self.client.get('/no-such-page/')
        self.assertContains(response, 'Page not found', status_code=404)
        self.assertContains(response, 'error-card', status_code=404)

    def test_server_error_page_does_not_touch_the_database(self):
        with self.assertNumQueries(0):
            response = errors.server_error(RequestFactory().get('/'))
        self.assertContains(response, 'Something went wrong', status_code=500)

    def test_crashing_view_shows_custom_500(self):
        self.client.raise_request_exception = False
        with patch('main.views.Advertisement.objects.filter', side_effect=RuntimeError('secret detail')):
            response = self.client.get(reverse('home'))
        self.assertContains(response, 'error-card', status_code=500)
        self.assertNotContains(response, 'secret detail', status_code=500)

    def test_csrf_failure_shows_custom_page(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse('authentication:login_submit'))
        self.assertContains(response, 'Session expired', status_code=403)

    def test_empty_error_response_is_filled_in_for_browsers(self):
        response = self.client.post(reverse('static_sitemap'), headers={'accept': 'text/html'})
        self.assertContains(response, 'Action not allowed', status_code=405)
        self.assertEqual(response['Allow'], 'GET')

    def test_empty_error_response_is_left_alone_for_fetch_callers(self):
        response = self.client.post(reverse('static_sitemap'), headers={'accept': '*/*'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'')

    def test_unlisted_status_uses_generic_message(self):
        response = errors.error_response(418)
        self.assertContains(response, 'complete your request', status_code=418)
