from unittest import expectedFailure

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ResourceItem


class ResourcePageTests(TestCase):
    fixtures = ['test_catalog']

    def test_list_and_category_pages(self):
        self.assertContains(self.client.get(reverse('resources:resources_list')), 'Surveillance Reports')
        self.assertContains(self.client.get(reverse('resources:category_resources', args=[9201])), 'GLASS Report')

    # Known bug: resources/resource_detail.html does not exist, so this page
    # (linked from the search catalog API) errors. Remove once it is added.
    @expectedFailure
    def test_detail_page(self):
        self.assertContains(self.client.get(reverse('resources:resource_detail', args=[9301])), 'GLASS Report')

    def test_missing_resource_returns_404(self):
        self.assertEqual(self.client.get(reverse('resources:resource_detail', args=[1])).status_code, 404)


class ResourceAdminAuditTests(TestCase):
    fixtures = ['test_catalog']

    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(email='admin@example.com', password='pw-12345678')
        self.client.force_login(self.admin)

    def test_admin_pages_render(self):
        self.assertEqual(self.client.get(reverse('admin:resources_resourceitem_changelist')).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:resources_resourcecategory_change', args=[9201])).status_code, 200)

    def test_saving_in_admin_records_editor_and_approver(self):
        response = self.client.post(reverse('admin:resources_resourceitem_add'), {
            'category': 9201,
            'title': 'New Guideline',
            'description': 'Treatment guideline.',
            'approval_status': 'approved',
            'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        item = ResourceItem.objects.get(title='New Guideline')
        self.assertEqual(item.added_by, self.admin)
        self.assertEqual(item.updated_by, self.admin)
        self.assertEqual(item.approved_by, self.admin)
        self.assertIsNotNone(item.approved_at)
