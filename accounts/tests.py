from pathlib import Path

from django.conf import settings
from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse

from departments.models import Department
from .models import User


class AccountUrlTests(TestCase):
    def test_superadmin_dashboard_url_name_resolves(self):
        self.assertEqual(reverse('superadmin_dashboard'), '/accounts/superadmin/')

    def test_login_required_redirect_uses_real_login_url(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/dashboard/')

    def test_login_page_does_not_show_demo_account_cards(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test accounts')
        self.assertNotContains(response, 'Admin@123')

    def test_about_page_omits_old_submission_date(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '18-02-2026')


class TemplateSyntaxTests(TestCase):
    def test_project_templates_compile(self):
        template_paths = []
        for path in Path(settings.BASE_DIR).rglob('templates/*.html'):
            template_paths.append(path)
        for path in Path(settings.BASE_DIR).rglob('templates/**/*.html'):
            template_paths.append(path)

        seen = set()
        for path in sorted(set(template_paths)):
            parts = path.parts
            template_index = len(parts) - 1 - parts[::-1].index('templates')
            template_name = '/'.join(parts[template_index + 1:])
            if template_name in seen:
                continue
            seen.add(template_name)
            with self.subTest(template=template_name):
                get_template(template_name)


class DepartmentAllocationTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name='Roads DSCC',
            slug='roads',
            city_corp='DSCC',
            is_active=True,
        )
        self.super_admin = User.objects.create_user(
            username='superadmin',
            password='pass123',
            role='super_admin',
        )
        self.admin = User.objects.create_user(
            username='dept-admin',
            password='pass123',
            role='admin',
        )
        self.worker = User.objects.create_user(
            username='worker',
            password='pass123',
            role='worker',
        )

    def test_super_admin_can_allocate_department_to_user(self):
        self.client.force_login(self.super_admin)

        response = self.client.post(
            reverse('update_user_department', args=[self.worker.pk]),
            {'department': self.department.pk},
        )

        self.assertRedirects(response, reverse('admin_users'))
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.department, self.department)

    def test_department_admin_cannot_allocate_departments(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('update_user_department', args=[self.worker.pk]),
            {'department': self.department.pk},
        )

        self.assertRedirects(response, reverse('admin_users'))
        self.worker.refresh_from_db()
        self.assertIsNone(self.worker.department)
