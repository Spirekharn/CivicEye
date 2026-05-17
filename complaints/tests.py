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


# ---------------------------------------------------------------------------
# Anonymous Alias Tests
# ---------------------------------------------------------------------------

class AnonymousAliasTests(TestCase):
    def setUp(self):
        self.citizen = User.objects.create_user(
            username='anoncitizen', password='testpass99', role='citizen'
        )
        self.dept = Department.objects.create(
            name='Roads DSCC', slug='roads', city_corp='DSCC', is_active=True
        )

    def _make_complaint(self, anonymous):
        return Complaint.objects.create(
            citizen=self.citizen,
            title='Test complaint',
            description='Description.',
            category='roads',
            city_corp='DSCC',
            location_text='Dhanmondi',
            is_anonymous=anonymous,
        )

    def test_alias_generated_for_anonymous_complaint(self):
        c = self._make_complaint(anonymous=True)
        self.assertTrue(c.anonymous_alias.startswith('Anon #'))
        self.assertEqual(len(c.anonymous_alias), 10)  # "Anon #" (6) + 4 chars

    def test_no_alias_for_non_anonymous_complaint(self):
        c = self._make_complaint(anonymous=False)
        self.assertEqual(c.anonymous_alias, '')

    def test_alias_uniqueness_across_ten_complaints(self):
        aliases = set()
        for _ in range(10):
            c = self._make_complaint(anonymous=True)
            self.assertNotIn(c.anonymous_alias, aliases)
            aliases.add(c.anonymous_alias)
        self.assertEqual(len(aliases), 10)

    def test_alias_not_overwritten_on_resave(self):
        c = self._make_complaint(anonymous=True)
        original = c.anonymous_alias
        c.description = 'Updated.'
        c.save()
        c.refresh_from_db()
        self.assertEqual(c.anonymous_alias, original)


# ---------------------------------------------------------------------------
# Duplicate Detection Tests
# ---------------------------------------------------------------------------

class DuplicateDetectionTests(TestCase):
    def setUp(self):
        self.citizen  = User.objects.create_user(
            username='dup_citizen', password='testpass99', role='citizen'
        )
        self.citizen2 = User.objects.create_user(
            username='dup_citizen2', password='testpass99', role='citizen'
        )
        self.dept = Department.objects.create(
            name='Roads DSCC', slug='roads', city_corp='DSCC', is_active=True
        )

    def _post_complaint(self, user, lat, lon):
        self.client.force_login(user)
        response = self.client.post(
            reverse('complaint_create'),
            {
                'title': 'Pothole on road',
                'description': 'Big pothole.',
                'category': 'roads',
                'priority': 'medium',
                'location_text': 'Dhanmondi Road 27',
                'latitude': lat,
                'longitude': lon,
            },
        )
        return response

    def test_complaints_40m_apart_marked_as_duplicate(self):
        # Submit first complaint
        self._post_complaint(self.citizen, 23.7465, 90.3760)
        primary = Complaint.objects.filter(citizen=self.citizen).first()
        self.assertFalse(primary.is_duplicate)

        # Submit second complaint ~40m away (same category, same time window)
        # 40m ≈ 0.00036 degrees latitude
        self._post_complaint(self.citizen2, 23.7468, 90.3761)
        secondary = Complaint.objects.filter(citizen=self.citizen2).first()
        secondary.refresh_from_db()
        self.assertTrue(secondary.is_duplicate)
        self.assertEqual(secondary.duplicate_of, primary)

    def test_complaints_4km_apart_not_marked_as_duplicate(self):
        self._post_complaint(self.citizen, 23.7465, 90.3760)
        # 4km ≈ 0.036 degrees latitude
        self._post_complaint(self.citizen2, 23.7825, 90.3760)
        secondary = Complaint.objects.filter(citizen=self.citizen2).first()
        secondary.refresh_from_db()
        self.assertFalse(secondary.is_duplicate)


# ---------------------------------------------------------------------------
# Access Control Tests
# ---------------------------------------------------------------------------

class AccessControlTests(TestCase):
    def setUp(self):
        self.dept  = Department.objects.create(
            name='Roads DSCC', slug='roads', city_corp='DSCC', is_active=True
        )
        self.dept2 = Department.objects.create(
            name='Roads DNCC', slug='roads', city_corp='DNCC', is_active=True
        )
        self.citizen  = User.objects.create_user(
            username='acc_citizen', password='testpass99', role='citizen'
        )
        self.surveyor = User.objects.create_user(
            username='acc_surveyor', password='testpass99',
            role='surveyor', department=self.dept
        )
        self.finance_user = User.objects.create_user(
            username='acc_finance', password='testpass99', role='finance'
        )
        self.admin = User.objects.create_user(
            username='acc_admin', password='testpass99',
            role='admin', department=self.dept
        )
        self.complaint = Complaint.objects.create(
            citizen=self.citizen,
            department=self.dept,
            title='Access test complaint',
            description='Testing.',
            category='roads',
            city_corp='DSCC',
            location_text='Dhanmondi',
            status='submitted',
        )

    def test_unassigned_surveyor_redirected_from_complaint_detail(self):
        """Surveyor not assigned to this complaint cannot view it."""
        self.client.force_login(self.surveyor)
        response = self.client.get(reverse('complaint_detail', args=[self.complaint.pk]))
        self.assertEqual(response.status_code, 302)

    def test_finance_blocked_from_assign_view(self):
        self.client.force_login(self.finance_user)
        response = self.client.get(reverse('assign_complaint', args=[self.complaint.pk]))
        self.assertRedirects(response, reverse('dashboard'))

    def test_complaint_auto_routes_to_correct_department(self):
        from complaints.location_router import get_department_for_complaint, detect_city_corp
        corp = detect_city_corp('Dhanmondi Road 27')
        self.assertEqual(corp, 'DSCC')
        dept = get_department_for_complaint('roads', 'DSCC')
        self.assertEqual(dept, self.dept)


# ---------------------------------------------------------------------------
# Community Dashboard Tests
# ---------------------------------------------------------------------------

class CommunityDashboardTests(TestCase):
    """
    Tests for the public community complaint explorer.
    Covers: accessibility without login, privacy boundaries,
    search/filter behaviour, and the public detail page.
    """

    def setUp(self):
        self.dept = Department.objects.create(
            name='Roads DSCC', slug='roads', city_corp='DSCC', is_active=True
        )
        self.citizen = User.objects.create_user(
            username='comm_citizen', password='testpass99', role='citizen',
            email='comm_citizen@example.com',
        )
        self.anon_citizen = User.objects.create_user(
            username='comm_anon', password='testpass99', role='citizen',
            email='comm_anon@example.com',
        )
        # A normal (non-anonymous) complaint
        self.complaint = Complaint.objects.create(
            citizen=self.citizen,
            department=self.dept,
            title='Broken road near school',
            description='Large pothole causing accidents.',
            category='roads',
            city_corp='DSCC',
            location_text='Dhanmondi Road 7',
            status='in_progress',
        )
        # An anonymous complaint
        self.anon_complaint = Complaint.objects.create(
            citizen=self.anon_citizen,
            department=self.dept,
            title='Sewage overflow near market',
            description='Drain blocked for two weeks.',
            category='sanitation',
            city_corp='DSCC',
            location_text='Mirpur 10',
            status='submitted',
            is_anonymous=True,
        )

    # ------------------------------------------------------------------ #
    # Accessibility                                                         #
    # ------------------------------------------------------------------ #

    def test_community_list_accessible_without_login(self):
        """Public list must render 200 for unauthenticated visitors."""
        response = self.client.get(reverse('community_list'))
        self.assertEqual(response.status_code, 200)

    def test_community_detail_accessible_without_login(self):
        """Public detail must render 200 for unauthenticated visitors."""
        response = self.client.get(reverse('community_detail', args=[self.complaint.pk]))
        self.assertEqual(response.status_code, 200)

    def test_community_list_accessible_when_logged_in(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('community_list'))
        self.assertEqual(response.status_code, 200)

    def test_community_detail_404_for_nonexistent_pk(self):
        response = self.client.get(reverse('community_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------ #
    # Privacy — list page                                                  #
    # ------------------------------------------------------------------ #

    def test_list_does_not_expose_citizen_username(self):
        """The community list must not contain the real citizen's username."""
        response = self.client.get(reverse('community_list'))
        self.assertNotContains(response, self.citizen.username)
        self.assertNotContains(response, self.citizen.email)

    def test_list_shows_complaint_titles(self):
        response = self.client.get(reverse('community_list'))
        self.assertContains(response, 'Broken road near school')
        self.assertContains(response, 'Sewage overflow near market')

    # ------------------------------------------------------------------ #
    # Privacy — detail page (non-anonymous complaint)                      #
    # ------------------------------------------------------------------ #

    def test_detail_does_not_expose_citizen_username(self):
        """Non-anonymous complaint detail must not reveal the real username."""
        response = self.client.get(reverse('community_detail', args=[self.complaint.pk]))
        self.assertNotContains(response, self.citizen.username)
        self.assertNotContains(response, self.citizen.email)

    def test_detail_shows_community_member_label_for_non_anonymous(self):
        """Non-anonymous reporter label must be 'Community Member'."""
        response = self.client.get(reverse('community_detail', args=[self.complaint.pk]))
        self.assertContains(response, 'Community Member')

    # ------------------------------------------------------------------ #
    # Privacy — detail page (anonymous complaint)                          #
    # ------------------------------------------------------------------ #

    def test_anonymous_complaint_shows_alias_not_real_name(self):
        """Anonymous complaint detail must show the alias, not the real username."""
        response = self.client.get(
            reverse('community_detail', args=[self.anon_complaint.pk])
        )
        self.assertNotContains(response, self.anon_citizen.username)
        alias = self.anon_complaint.anonymous_alias
        self.assertTrue(alias.startswith('Anon #'), f"Expected alias to start with 'Anon #', got: {alias!r}")
        self.assertContains(response, alias)

    def test_anonymous_complaint_does_not_contain_community_member_label(self):
        """Anonymous complaints must not fall through to 'Community Member' label."""
        response = self.client.get(
            reverse('community_detail', args=[self.anon_complaint.pk])
        )
        self.assertNotContains(response, 'Community Member')

    # ------------------------------------------------------------------ #
    # Search                                                               #
    # ------------------------------------------------------------------ #

    def test_search_by_title_returns_matching_complaint(self):
        response = self.client.get(reverse('community_list'), {'q': 'Broken road'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Broken road near school')
        self.assertNotContains(response, 'Sewage overflow near market')

    def test_search_no_match_shows_empty_state(self):
        response = self.client.get(reverse('community_list'), {'q': 'xyznonexistent'})
        self.assertContains(response, 'No complaints found')

    # ------------------------------------------------------------------ #
    # Filters                                                              #
    # ------------------------------------------------------------------ #

    def test_category_filter_limits_results(self):
        response = self.client.get(reverse('community_list'), {'category': 'sanitation'})
        self.assertContains(response, 'Sewage overflow near market')
        self.assertNotContains(response, 'Broken road near school')

    def test_status_filter_limits_results(self):
        response = self.client.get(reverse('community_list'), {'status': 'submitted'})
        self.assertContains(response, 'Sewage overflow near market')
        self.assertNotContains(response, 'Broken road near school')

    def test_city_corp_filter_limits_results(self):
        """All complaints in this setUp are DSCC; CCC filter should give empty."""
        response = self.client.get(reverse('community_list'), {'city_corp': 'CCC'})
        self.assertNotContains(response, 'Broken road near school')

    def test_invalid_category_filter_ignored(self):
        """An unrecognised category value must not crash the view."""
        response = self.client.get(reverse('community_list'), {'category': 'INVALID_VALUE'})
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------ #
    # Content checks — detail page                                         #
    # ------------------------------------------------------------------ #

    def test_detail_shows_full_description(self):
        response = self.client.get(reverse('community_detail', args=[self.complaint.pk]))
        self.assertContains(response, 'Large pothole causing accidents.')

    def test_detail_shows_city_corp_and_category(self):
        response = self.client.get(reverse('community_detail', args=[self.complaint.pk]))
        self.assertContains(response, 'DSCC')
        self.assertContains(response, 'Roads')

    def test_detail_shows_location_text(self):
        response = self.client.get(reverse('community_detail', args=[self.complaint.pk]))
        self.assertContains(response, 'Dhanmondi Road 7')

    def test_detail_does_not_contain_internal_finance_data(self):
        """
        Public detail must not mention internal budget amounts or
        approval/rejection finance details.
        """
        response = self.client.get(reverse('community_detail', args=[self.complaint.pk]))
        self.assertNotContains(response, 'allocated_amount')
        self.assertNotContains(response, 'fiscal_year')

    # ------------------------------------------------------------------ #
    # Duplicate complaint notice                                           #
    # ------------------------------------------------------------------ #

    def test_duplicate_complaint_shows_notice(self):
        duplicate = Complaint.objects.create(
            citizen=self.citizen,
            title='Another broken road',
            description='Same area pothole.',
            category='roads',
            city_corp='DSCC',
            location_text='Dhanmondi Road 7',
            status='submitted',
            is_duplicate=True,
            duplicate_of=self.complaint,
        )
        response = self.client.get(reverse('community_detail', args=[duplicate.pk]))
        self.assertContains(response, 'duplicate')
        self.assertContains(response, str(self.complaint.pk))
