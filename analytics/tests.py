import json

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from departments.models import Department
from complaints.models import Complaint


class AnalyticsAccessTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name='Roads DSCC', slug='roads', city_corp='DSCC', is_active=True
        )
        self.citizen = User.objects.create_user(
            username='ana_citizen', password='testpass99', role='citizen'
        )
        self.admin = User.objects.create_user(
            username='ana_admin', password='testpass99',
            role='admin', department=self.dept
        )
        self.finance_user = User.objects.create_user(
            username='ana_finance', password='testpass99', role='finance'
        )
        self.super_admin = User.objects.create_user(
            username='ana_super', password='testpass99', role='super_admin'
        )

    def test_analytics_dashboard_requires_login(self):
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_super_admin_can_access_dashboard(self):
        self.client.force_login(self.super_admin)
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_finance_can_access_dashboard(self):
        self.client.force_login(self.finance_user)
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_citizen_redirected_from_dashboard(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertRedirects(response, reverse('dashboard'))

    def _api_get(self, url_name):
        return self.client.get(reverse(url_name))

    def test_api_by_category_returns_data_key(self):
        self.client.force_login(self.super_admin)
        response = self._api_get('api_by_category')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertIn('data', payload)

    def test_api_by_status_returns_data_key(self):
        self.client.force_login(self.super_admin)
        response = self._api_get('api_by_status')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertIn('data', payload)

    def test_api_resolution_trend_returns_data_key(self):
        self.client.force_login(self.super_admin)
        response = self._api_get('api_resolution_trend')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertIn('data', payload)

    def test_api_budget_utilisation_forbidden_for_admin(self):
        self.client.force_login(self.admin)
        response = self._api_get('api_budget_utilisation')
        self.assertEqual(response.status_code, 403)

    def test_api_budget_utilisation_allowed_for_finance(self):
        self.client.force_login(self.finance_user)
        response = self._api_get('api_budget_utilisation')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertIn('data', payload)
        self.assertIn('fiscal_year', payload)
