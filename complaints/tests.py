from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from departments.models import Department
from finance.models import Expense
from .models import Complaint, ComplaintFeedback, SurveyReport


class ComplaintWorkflowTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name='Roads DSCC',
            slug='roads',
            city_corp='DSCC',
            is_active=True,
        )
        self.other_dept = Department.objects.create(
            name='Roads DNCC',
            slug='roads',
            city_corp='DNCC',
            is_active=True,
        )
        self.citizen = User.objects.create_user(username='citizen', password='pass123', role='citizen')
        self.surveyor = User.objects.create_user(
            username='surveyor',
            password='pass123',
            role='surveyor',
            department=self.dept,
        )
        self.other_surveyor = User.objects.create_user(
            username='other-surveyor',
            password='pass123',
            role='surveyor',
            department=self.other_dept,
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='pass123',
            role='admin',
            department=self.dept,
        )
        self.other_worker = User.objects.create_user(
            username='other-worker',
            password='pass123',
            role='worker',
            department=self.other_dept,
        )
        self.complaint = Complaint.objects.create(
            citizen=self.citizen,
            department=self.dept,
            title='Broken road',
            description='A dangerous pothole needs repair.',
            category='roads',
            city_corp='DSCC',
            location_text='Dhanmondi',
            assigned_surveyor=self.surveyor,
            status='resolved',
        )

    def test_detail_renders_related_survey_and_feedback(self):
        SurveyReport.objects.create(
            complaint=self.complaint,
            surveyor=self.surveyor,
            findings='Needs resurfacing.',
            estimated_cost=Decimal('1200.00'),
        )
        ComplaintFeedback.objects.create(
            complaint=self.complaint,
            citizen=self.citizen,
            rating=5,
            comment='Handled well.',
        )

        self.client.force_login(self.citizen)
        response = self.client.get(reverse('complaint_detail', args=[self.complaint.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Survey Report')
        self.assertContains(response, 'Your Feedback')

    def test_surveyor_cannot_view_unassigned_complaint(self):
        self.client.force_login(self.other_surveyor)

        response = self.client.get(reverse('complaint_detail', args=[self.complaint.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complaint_list'))

    def test_assign_worker_rejects_worker_from_another_department(self):
        Expense.objects.create(
            title='Estimate',
            department=self.dept,
            complaint=self.complaint,
            amount=Decimal('1000.00'),
            status='approved',
        )
        self.complaint.status = 'budget_approved'
        self.complaint.save(update_fields=['status'])

        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('assign_worker', args=[self.complaint.pk]),
            {'worker': self.other_worker.pk},
        )

        self.assertEqual(response.status_code, 404)
        self.complaint.refresh_from_db()
        self.assertIsNone(self.complaint.assigned_worker)

    def test_invalid_survey_estimate_returns_form(self):
        self.complaint.status = 'surveying'
        self.complaint.save(update_fields=['status'])

        self.client.force_login(self.surveyor)
        response = self.client.post(
            reverse('submit_survey', args=[self.complaint.pk]),
            {
                'findings': 'Needs work.',
                'labor_estimate': 'not-a-number',
                'equipment_estimate': '0',
                'misc_estimate': '0',
                'estimated_days': '3',
                'priority_recommendation': 'medium',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(SurveyReport.objects.filter(complaint=self.complaint).exists())

    def test_create_complaint_accepts_priority_and_department(self):
        self.client.force_login(self.citizen)

        response = self.client.post(
            reverse('complaint_create'),
            {
                'title': 'Street light broken',
                'description': 'The light is out near the crossing.',
                'category': 'electricity',
                'department': self.dept.pk,
                'priority': 'high',
                'location_text': 'Dhanmondi',
            },
        )

        complaint = Complaint.objects.get(title='Street light broken')
        self.assertRedirects(response, reverse('complaint_detail', args=[complaint.pk]))
        self.assertEqual(complaint.department, self.dept)
        self.assertEqual(complaint.priority, 'high')

    def test_admin_can_assign_own_department_to_unassigned_complaint(self):
        complaint = Complaint.objects.create(
            citizen=self.citizen,
            title='Unassigned issue',
            description='Needs routing.',
            category='roads',
            city_corp='DSCC',
            location_text='Unknown area',
            department=None,
            status='submitted',
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('assign_complaint', args=[complaint.pk]),
            {'department': self.dept.pk, 'priority': 'critical'},
        )

        self.assertRedirects(response, reverse('assign_complaint', args=[complaint.pk]))
        complaint.refresh_from_db()
        self.assertEqual(complaint.department, self.dept)
        self.assertEqual(complaint.priority, 'critical')
        self.assertEqual(complaint.status, 'under_review')
