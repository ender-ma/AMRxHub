import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Tool, ToolCategory, ToolClick
from .tracking import click_statistics

BROWSER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'


class ToolClickTrackingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.category = ToolCategory.objects.create(name='Genomics', description='d')
        self.tool = Tool.objects.create(
            name='BLAST', description='d', short_description='s',
            category=self.category, url='https://example.com/',
        )

    def click(self, ip='1.2.3.4', agent=BROWSER):
        return self.client.get(
            reverse('tools:tool_access', args=[self.tool.id]),
            HTTP_USER_AGENT=agent, REMOTE_ADDR=ip,
        )

    def test_click_is_recorded_anonymously(self):
        user = get_user_model().objects.create_user(email='u@example.com', password='pw')
        self.client.force_login(user)
        response = self.click()
        self.assertEqual(response.status_code, 302)
        click = ToolClick.objects.get()
        self.assertIsNone(click.user)
        self.assertIsNone(click.ip_address)
        self.assertEqual(len(click.visitor_hash), 64)
        self.tool.refresh_from_db()
        self.assertEqual(self.tool.click_count, 1)

    def test_repeat_clicks_from_same_visitor_count_once(self):
        self.click()
        self.click()
        self.click(ip='5.6.7.8')
        self.assertEqual(ToolClick.objects.count(), 2)

    def test_bots_are_ignored(self):
        self.click(agent='Googlebot/2.1')
        self.click(agent='')
        self.assertEqual(ToolClick.objects.count(), 0)

    def test_forwarded_ip_distinguishes_visitors_behind_proxy(self):
        url = reverse('tools:tool_access', args=[self.tool.id])
        self.client.get(url, HTTP_USER_AGENT=BROWSER, HTTP_X_FORWARDED_FOR='9.9.9.1, 10.0.0.1')
        self.client.get(url, HTTP_USER_AGENT=BROWSER, HTTP_X_FORWARDED_FOR='9.9.9.2, 10.0.0.1')
        self.assertEqual(ToolClick.objects.count(), 2)

    def test_statistics_by_period(self):
        now = timezone.now()
        for days_ago in (0, 0, 3, 20, 40):
            c = ToolClick.objects.create(tool=self.tool, visitor_hash=f'h{days_ago}')
            ToolClick.objects.filter(pk=c.pk).update(timestamp=now - timedelta(days=days_ago))
        stats = click_statistics()
        today, week, month = (p['clicks'] for p in stats['periods'])
        self.assertEqual((today, week, month), (2, 3, 4))
        self.assertEqual(stats['all_time'], 5)
        self.assertEqual(stats['periods'][2]['top_tools'][0]['total'], 4)
        self.assertEqual(sum(d['total'] for d in stats['trend']), 4)

    def test_admin_click_page_renders(self):
        admin_user = get_user_model().objects.create_superuser(email='a@example.com', password='pw')
        self.client.force_login(admin_user)
        self.click()
        response = self.client.get(reverse('admin:tools_toolclick_changelist'))
        self.assertContains(response, 'Tool usage')
        self.assertContains(response, 'BLAST')
        response = self.client.get(reverse('admin:tools_tool_changelist'))
        self.assertContains(response, 'Clicks (7d)')


class ToolPageTests(TestCase):
    fixtures = ['test_catalog']

    def test_home_shows_featured_tool(self):
        response = self.client.get(reverse('tools:tools_home'))
        self.assertContains(response, 'ResFinder')
        self.assertContains(response, 'Escherichia coli')

    def test_category_lists_only_public_tools(self):
        response = self.client.get(reverse('tools:category_tools', args=[9002]))
        self.assertContains(response, 'ResFinder')
        self.assertContains(response, 'AMRFinderPlus')
        self.assertNotContains(response, 'Pending Example Tool')
        self.assertNotContains(response, 'Retired Example Tool')

    def test_detail_hides_unapproved_and_inactive_tools(self):
        self.assertContains(self.client.get(reverse('tools:tool_detail', args=[9101])), 'ResFinder')
        for pk in (9103, 9104):
            with self.subTest(tool=pk):
                self.assertEqual(self.client.get(reverse('tools:tool_detail', args=[pk])).status_code, 404)

    def test_access_redirects_to_tool_site(self):
        response = self.client.get(reverse('tools:tool_access', args=[9101]), HTTP_USER_AGENT=BROWSER)
        self.assertRedirects(response, 'https://genepi.food.dtu.dk/resfinder', fetch_redirect_response=False)


@override_settings(TOOL_FLAG_EMAIL='flags@example.com')
class FlagToolTests(TestCase):
    fixtures = ['test_catalog']

    def setUp(self):
        cache.clear()
        self.url = reverse('flag_tool')

    def post(self, data):
        return self.client.post(self.url, json.dumps(data), content_type='application/json')

    def test_requires_login(self):
        self.assertEqual(self.post({'tool_id': 9101, 'reason': 'Broken link'}).status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_flag_emails_admins(self):
        user = get_user_model().objects.create_user(email='flagger@example.com', password='pw-12345678')
        self.client.force_login(user)
        self.assertEqual(self.post({'tool_id': 9101, 'reason': ''}).status_code, 400)
        response = self.post({'tool_id': 9101, 'reason': 'Broken link'})
        self.assertTrue(response.json()['success'])
        self.assertEqual(mail.outbox[0].to, ['flags@example.com'])
        self.assertIn('ResFinder', mail.outbox[0].subject)
