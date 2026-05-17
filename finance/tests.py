from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from departments.models import Department
from complaints.models import Complaint
from finance.models import DepartmentBudget, Expense, get_fiscal_year


class FinanceWorkflowTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name='Roads DSCC', slug='roads', city_corp='DSCC', is_active=True
        )
        self.citizen = User.objects.create_user(
            username='fin_citizen', password='testpass99', role='citizen'
        )
        self.finance_user = User.objects.create_user(
            username='fin_finance', password='testpass99', role='finance'
        )
        self.admin = User.objects.create_user(
            username='fin_admin', password='testpass99',
            role='admin', department=self.dept
        )
        self.super_admin = User.objects.create_user(
            username='fin_super', password='testpass99', role='super_admin'
        )
        self.complaint = Complaint.objects.create(
            citizen=self.citizen,
            department=self.dept,
            title='Finance test complaint',
            description='Needs budget.',
            category='roads',
            city_corp='DSCC',
            location_text='Dhanmondi',
            status='budget_pending',
        )
        DepartmentBudget.objects.create(
            department=self.dept,
            fiscal_year=get_fiscal_year(),
            allocated_amount=Decimal('100000.00'),
        )
        self.expense = Expense.objects.create(
            title='Road repair estimate',
            department=self.dept,
            complaint=self.complaint,
            amount=Decimal('50000.00'),
            fiscal_year=get_fiscal_year(),
            status='pending',
        )

    def test_approve_advances_complaint_to_budget_approved(self):
        self.client.force_login(self.finance_user)
        response = self.client.post(
            reverse('approve_expense', args=[self.expense.pk]),
            {'action': 'approve'},
        )
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.status, 'approved')
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, 'budget_approved')

    def test_reject_sets_expense_status_to_rejected(self):
        self.client.force_login(self.finance_user)
        response = self.client.post(
            reverse('approve_expense', args=[self.expense.pk]),
            {'action': 'reject', 'reason': 'Over budget.'},
        )
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.status, 'rejected')

    def test_citizen_redirected_from_finance_dashboard(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('finance_dashboard'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_dept_admin_blocked_from_allocate_budget(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('allocate_budget'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_finance_can_view_expense_list(self):
        self.client.force_login(self.finance_user)
        response = self.client.get(reverse('expense_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Road repair estimate')
