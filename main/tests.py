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


class GlossaryTests(TestCase):
    """The glossary is seeded by migration 0008 and managed in the Django admin."""

    def glossary_payload(self):
        response = self.client.get(reverse('glossary'))
        self.assertEqual(response.status_code, 200)
        return response.context['glossary_data']

    def test_seeded_terms_are_shown(self):
        from main.models import GlossaryTerm
        self.assertEqual(GlossaryTerm.objects.count(), 27)
        data = self.glossary_payload()
        self.assertEqual(len(data['terms']), 27)
        self.assertEqual([c['id'] for c in data['categories']], ['core', 'technical', 'genetics', 'additional'])
        self.assertIn('plasmid', {t['id'] for t in data['terms']})

    def test_only_published_terms_are_shown(self):
        from main.models import GlossaryTerm
        GlossaryTerm.objects.filter(slug='plasmid').update(approval_status='pending')
        GlossaryTerm.objects.filter(slug='biofilm').update(is_active=False)
        ids = {t['id'] for t in self.glossary_payload()['terms']}
        self.assertNotIn('plasmid', ids)
        self.assertNotIn('biofilm', ids)
        self.assertIn('mutation', ids)

    def test_admin_added_term_appears_with_details(self):
        from main.models import GlossaryCategory, GlossaryTerm
        core = GlossaryCategory.objects.get(slug='core')
        term = GlossaryTerm.objects.create(
            category=core, term='Minimum Inhibitory Concentration', abbreviation='MIC',
            definition='Lowest concentration that prevents visible growth.',
            context='Used in susceptibility testing.', references='CLSI M100\n\nEUCAST breakpoints',
        )
        term.related_terms.add(GlossaryTerm.objects.get(slug='amr'))
        self.assertEqual(term.slug, 'mic')  # auto-filled from the abbreviation
        entry = next(t for t in self.glossary_payload()['terms'] if t['id'] == 'mic')
        self.assertEqual(entry['references'], ['CLSI M100', 'EUCAST breakpoints'])
        self.assertEqual(entry['related'], ['amr'])

    def test_page_renders_terms_from_the_database(self):
        # Guards against the template falling back to a hard-coded word list
        from main.models import GlossaryCategory, GlossaryTerm
        GlossaryTerm.objects.create(category=GlossaryCategory.objects.get(slug='core'),
                                    term='Carbapenemase', definition='Enzyme that breaks down carbapenems.')
        response = self.client.get(reverse('glossary'))
        self.assertContains(response, 'id="glossary-data"')
        self.assertContains(response, 'Carbapenemase')

    def test_term_text_is_not_rendered_as_html(self):
        from main.models import GlossaryCategory, GlossaryTerm
        GlossaryTerm.objects.create(category=GlossaryCategory.objects.get(slug='core'),
                                    term='<script>alert(1)</script>', definition='x')
        response = self.client.get(reverse('glossary'))
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_admin_save_stamps_audit_fields(self):
        from main.models import GlossaryCategory, GlossaryTerm
        admin_user = get_user_model().objects.create_superuser(email='admin@example.com', password='pw-12345678')
        self.client.force_login(admin_user)
        response = self.client.post(reverse('admin:main_glossaryterm_add'), {
            'category': GlossaryCategory.objects.get(slug='core').pk,
            'term': 'Colistin', 'slug': '', 'abbreviation': '', 'definition': 'A last-resort polymyxin antibiotic.',
            'context': '', 'references': '', 'approval_status': 'approved', 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        term = GlossaryTerm.objects.get(term='Colistin')
        self.assertEqual(term.added_by, admin_user)
        self.assertEqual(term.approved_by, admin_user)
        self.assertIsNotNone(term.approved_at)
