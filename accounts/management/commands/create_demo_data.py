"""
accounts/management/commands/create_demo_data.py
Run with: python manage.py create_demo_data

Creates realistic test accounts and simulates full complaint workflows
including duplicates, transfers, budget approvals, rejections, and feedback.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from complaints.models import (
    Complaint, ComplaintStatusHistory, ComplaintTransferRequest,
    SurveyReport, ComplaintFeedback, CATEGORY_CHOICES
)
from departments.models import Department
from finance.models import DepartmentBudget, Expense, get_fiscal_year
from notifications.models import Notification


def _log(complaint, status, user, notes='', event_type='status_change'):
    ComplaintStatusHistory.objects.create(
        complaint=complaint, status=status, changed_by=user,
        notes=notes, event_type=event_type,
    )


def _notify(user, title, msg, ntype, complaint=None):
    Notification.objects.create(
        user=user, title=title, message=msg,
        notification_type=ntype, complaint=complaint,
    )


class Command(BaseCommand):
    help = 'Creates realistic demo accounts and simulates full complaint workflows'

    # ------------------------------------------------------------------ #
    #  helpers                                                             #
    # ------------------------------------------------------------------ #

    def _make_user(self, username, password, role, first, last,
                   dept=None, email=None, dept_head=False):
        u, created = User.objects.get_or_create(username=username)
        u.set_password(password)
        u.role = role
        u.first_name = first
        u.last_name = last
        u.email = email or f'{username}@civiceye.bd'
        u.department = dept
        u.is_department_head = dept_head
        u.is_active = True
        u.save()
        tag = 'Created' if created else 'Updated'
        self.stdout.write(f'  {tag}: {username} ({role})')
        return u

    def _dept(self, slug, corp):
        return Department.objects.filter(slug=slug, city_corp=corp, is_active=True).first()

    # ------------------------------------------------------------------ #
    #  main                                                                #
    # ------------------------------------------------------------------ #

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO('\n=== CivicEye Demo Data ===\n'))
        fiscal = get_fiscal_year()

        # ── reference departments ──────────────────────────────────────
        dscc_roads  = self._dept('roads',       'DSCC')
        dscc_water  = self._dept('water',       'DSCC')
        dscc_sanit  = self._dept('sanitation',  'DSCC')
        dscc_it     = self._dept('it',          'DSCC')
        dscc_elec   = self._dept('electricity', 'DSCC')
        dscc_env    = self._dept('environment', 'DSCC')
        dncc_roads  = self._dept('roads',       'DNCC')
        dncc_water  = self._dept('water',       'DNCC')
        dncc_sanit  = self._dept('sanitation',  'DNCC')

        if not dscc_roads:
            self.stdout.write(self.style.ERROR(
                'Departments not found. Run "python manage.py seed_data" first.'))
            return

        # ── budgets ────────────────────────────────────────────────────
        sa = User.objects.filter(role='super_admin').first()
        for dept, amount in [
            (dscc_roads, 8000000), (dscc_water, 6000000), (dscc_sanit, 4000000),
            (dscc_it, 3000000),    (dscc_elec, 5000000),  (dscc_env, 3500000),
            (dncc_roads, 7000000), (dncc_water, 5500000),
        ]:
            if dept:
                DepartmentBudget.objects.update_or_create(
                    department=dept, fiscal_year=fiscal,
                    defaults={'allocated_amount': amount, 'allocated_by': sa},
                )

        # ── finance officers ───────────────────────────────────────────
        self.stdout.write('\n[Finance Officers]')
        fin1 = self._make_user('mehedi_finance', 'Finance@2026', 'finance',
                               'Mehedi', 'Hasan', email='mehedi.fin@civiceye.bd')
        fin2 = self._make_user('nasrin_finance', 'Finance@2026', 'finance',
                               'Nasrin', 'Akter', email='nasrin.fin@civiceye.bd')

        # ── department admins + heads ──────────────────────────────────
        self.stdout.write('\n[Department Admins]')
        adm_dscc_roads = self._make_user(
            'rafiq_admin', 'Admin@2026', 'admin', 'Rafiqul', 'Islam',
            dept=dscc_roads, dept_head=True, email='rafiq@civiceye.bd')

        adm_dscc_it = self._make_user(
            'taslima_admin', 'Admin@2026', 'admin', 'Taslima', 'Begum',
            dept=dscc_it, dept_head=True, email='taslima@civiceye.bd')

        adm_dncc_roads = self._make_user(
            'karim_admin', 'Admin@2026', 'admin', 'Abdul', 'Karim',
            dept=dncc_roads, dept_head=False, email='karim@civiceye.bd')

        adm_dscc_water = self._make_user(
            'shabana_admin', 'Admin@2026', 'admin', 'Shabana', 'Khatun',
            dept=dscc_water, dept_head=True, email='shabana@civiceye.bd')

        # extra admin head for department head notification tests
        adm_dscc_sanit = self._make_user(
            'reza_admin', 'Admin@2026', 'admin', 'Reza', 'Chowdhury',
            dept=dscc_sanit, dept_head=False, email='reza@civiceye.bd')

        # ── surveyors ─────────────────────────────────────────────────
        self.stdout.write('\n[Surveyors]')
        sur1 = self._make_user('labib_surveyor',  'Survey@2026', 'surveyor',
                               'Labib', 'Ahmed',   dept=dscc_roads)
        sur2 = self._make_user('sadia_surveyor',  'Survey@2026', 'surveyor',
                               'Sadia', 'Islam',   dept=dscc_roads)
        sur3 = self._make_user('tamim_surveyor',  'Survey@2026', 'surveyor',
                               'Tamim', 'Iqbal',   dept=dscc_water)
        sur4 = self._make_user('mitu_surveyor',   'Survey@2026', 'surveyor',
                               'Mitu',  'Akhter',  dept=dncc_roads)
        sur5 = self._make_user('jahid_surveyor',  'Survey@2026', 'surveyor',
                               'Jahid', 'Hossain', dept=dscc_sanit)

        # ── workers ───────────────────────────────────────────────────
        self.stdout.write('\n[Field Workers]')
        wrk1 = self._make_user('lamiya_worker',   'Worker@2026', 'worker',
                               'Lamiya', 'Parvin',  dept=dscc_roads)
        wrk2 = self._make_user('arif_worker',     'Worker@2026', 'worker',
                               'Arif',   'Hossain', dept=dscc_roads)
        wrk3 = self._make_user('rokon_worker',    'Worker@2026', 'worker',
                               'Rokon',  'Uddin',   dept=dscc_water)
        wrk4 = self._make_user('sharmin_worker',  'Worker@2026', 'worker',
                               'Sharmin','Akter',   dept=dscc_sanit)
        wrk5 = self._make_user('mosharraf_worker','Worker@2026', 'worker',
                               'Mosharraf','Ali',   dept=dncc_roads)

        # ── technicians ───────────────────────────────────────────────
        self.stdout.write('\n[Technicians]')
        tech1 = self._make_user('sujan_tech',   'Tech@2026', 'technician',
                                'Sujan',   'Dey',     dept=dscc_it)
        tech2 = self._make_user('farida_tech',  'Tech@2026', 'technician',
                                'Farida',  'Khanam',  dept=dscc_it)
        tech3 = self._make_user('ripon_tech',   'Tech@2026', 'technician',
                                'Ripon',   'Islam',   dept=dscc_elec)
        tech4 = self._make_user('shirin_tech',  'Tech@2026', 'technician',
                                'Shirin',  'Akter',   dept=dscc_elec)
        tech5 = self._make_user('imran_tech',   'Tech@2026', 'technician',
                                'Imran',   'Chowdhury', dept=dscc_it)

        # ── 20 citizens ───────────────────────────────────────────────
        self.stdout.write('\n[Citizens]')
        citizen_data = [
            ('rahim_citizen',    'Citi@2026', 'Abdur',    'Rahim'),
            ('karim_citizen',    'Citi@2026', 'Abdul',    'Karim'),
            ('fatema_citizen',   'Citi@2026', 'Fatema',   'Begum'),
            ('rashida_citizen',  'Citi@2026', 'Rashida',  'Khatun'),
            ('monir_citizen',    'Citi@2026', 'Monir',    'Hossain'),
            ('sabrina_citizen',  'Citi@2026', 'Sabrina',  'Islam'),
            ('jakir_citizen',    'Citi@2026', 'Jakir',    'Hossain'),
            ('nasima_citizen',   'Citi@2026', 'Nasima',   'Parvin'),
            ('torikul_citizen',  'Citi@2026', 'Torikul',  'Islam'),
            ('kohinoor_citizen', 'Citi@2026', 'Kohinoor', 'Begum'),
            ('selim_citizen',    'Citi@2026', 'Selim',    'Reza'),
            ('rehana_citizen',   'Citi@2026', 'Rehana',   'Akter'),
            ('mofizur_citizen',  'Citi@2026', 'Mofizur',  'Rahman'),
            ('sultana_citizen',  'Citi@2026', 'Sultana',  'Khanam'),
            ('jahangir_citizen', 'Citi@2026', 'Jahangir', 'Alam'),
            ('hasina_citizen',   'Citi@2026', 'Hasina',   'Begum'),
            ('anwar_citizen',    'Citi@2026', 'Anwar',    'Hossain'),
            ('parveen_citizen',  'Citi@2026', 'Parveen',  'Akter'),
            ('rubel_citizen',    'Citi@2026', 'Rubel',    'Miah'),
            ('shiuly_citizen',   'Citi@2026', 'Shiuly',   'Akter'),
        ]
        citizens = []
        for uname, pw, fn, ln in citizen_data:
            citizens.append(self._make_user(uname, pw, 'citizen', fn, ln))

        c0, c1, c2, c3, c4 = citizens[0], citizens[1], citizens[2], citizens[3], citizens[4]
        c5, c6, c7, c8, c9 = citizens[5], citizens[6], citizens[7], citizens[8], citizens[9]
        c10, c11, c12, c13 = citizens[10], citizens[11], citizens[12], citizens[13]
        c14, c15, c16, c17 = citizens[14], citizens[15], citizens[16], citizens[17]
        c18, c19 = citizens[18], citizens[19]

        self.stdout.write(self.style.SUCCESS(f'\n  All accounts created.\n'))

        # ================================================================
        # COMPLAINT SCENARIOS
        # ================================================================
        self.stdout.write('[Creating Complaints & Workflows]\n')

        # helper to back-date complaints
        def backdate(c, days):
            Complaint.objects.filter(pk=c.pk).update(
                created_at=timezone.now() - timedelta(days=days),
                updated_at=timezone.now() - timedelta(days=days),
            )
            c.refresh_from_db()

        # ── 1. FULLY RESOLVED — pothole → surveyed → budget approved → worker resolved ──
        pot1 = Complaint.objects.create(
            citizen=c0, title='Deep pothole on Mirpur Road near Shia Masjid',
            description='A very large pothole has formed near the Shia Masjid junction on Mirpur Road. '
                        'Vehicles are swerving dangerously. The pothole is roughly 1.5m wide and 20cm deep.',
            category='roads', location_text='Mirpur Road, Mirpur, DSCC',
            latitude=23.8041, longitude=90.3658,
            city_corp='DSCC', department=dscc_roads,
            status='resolved', priority='high',
            assigned_surveyor=sur1, assigned_worker=wrk1,
            resolution_notes='Pothole filled with hot-mix asphalt. Road surface levelled and compacted.',
        )
        backdate(pot1, 30)
        _log(pot1, 'submitted', c0, 'Complaint submitted.')
        _log(pot1, 'under_review', adm_dscc_roads, 'Received and under review.')
        _log(pot1, 'assigned', adm_dscc_roads, f'Assigned to surveyor {sur1.get_full_name()}.')
        _log(pot1, 'surveying', sur1, 'Survey started.')
        _log(pot1, 'survey_done', sur1, 'Survey complete. Estimated cost BDT 85,000.')
        _log(pot1, 'budget_pending', sur1, 'Expense created, awaiting approval.')
        _log(pot1, 'budget_approved', fin1, f'Budget approved by {fin1.get_full_name()}.')
        _log(pot1, 'worker_assigned', adm_dscc_roads, f'Assigned to {wrk1.get_full_name()}.')
        _log(pot1, 'in_progress', wrk1, 'Work started.')
        _log(pot1, 'resolved', wrk1, 'Pothole repaired.')
        sr1 = SurveyReport.objects.create(
            complaint=pot1, surveyor=sur1,
            findings='Large pothole 150cm×80cm×20cm. Subgrade damaged. Requires full patching.',
            materials_needed='Hot-mix asphalt 500kg, tack coat, road roller.',
            labor_estimate=Decimal('35000'), equipment_estimate=Decimal('25000'),
            misc_estimate=Decimal('5000'), estimated_cost=Decimal('65000'),
            priority_recommendation='high', estimated_days=3,
        )
        exp1 = Expense.objects.create(
            title='Pothole repair — Mirpur Road', department=dscc_roads,
            complaint=pot1, amount=Decimal('65000'),
            fiscal_year=fiscal, status='approved', approved_by=fin1,
        )
        ComplaintFeedback.objects.create(complaint=pot1, citizen=c0, rating=4,
            comment='Fixed quickly! The road is smooth again. Thank you.')
        _notify(c0, 'Issue Resolved', f'Your complaint "{pot1.title}" has been resolved.', 'complaint_resolved', pot1)
        self.stdout.write('  [OK] Scenario 1: Fully resolved pothole (DSCC Roads)')

        # ── 2. RESOLVED WITH POOR RATING ──────────────────────────────
        drain1 = Complaint.objects.create(
            citizen=c1, title='Broken drain cover on Elephant Road causing flooding',
            description='The drain cover on Elephant Road near the fruit market is completely broken. '
                        'Every time it rains, sewage water floods onto the footpath and road.',
            category='water', location_text='Elephant Road, Dhanmondi, DSCC',
            latitude=23.7414, longitude=90.3800,
            city_corp='DSCC', department=dscc_water,
            status='resolved', priority='high',
            assigned_surveyor=sur3, assigned_worker=wrk3,
            resolution_notes='Drain cover replaced with reinforced iron grating.',
        )
        backdate(drain1, 45)
        _log(drain1, 'submitted', c1, 'Complaint submitted.')
        _log(drain1, 'assigned', adm_dscc_water, f'Surveyor {sur3.get_full_name()} assigned.')
        _log(drain1, 'survey_done', sur3, 'Survey complete.')
        _log(drain1, 'budget_approved', fin1, 'Budget approved.')
        _log(drain1, 'resolved', wrk3, 'Drain cover replaced.')
        SurveyReport.objects.create(
            complaint=drain1, surveyor=sur3,
            findings='Drain cover broken in 3 places. Needs full replacement.',
            labor_estimate=Decimal('8000'), equipment_estimate=Decimal('12000'),
            misc_estimate=Decimal('2000'), estimated_cost=Decimal('22000'),
            priority_recommendation='high', estimated_days=1,
        )
        Expense.objects.create(
            title='Drain cover replacement — Elephant Road', department=dscc_water,
            complaint=drain1, amount=Decimal('22000'),
            fiscal_year=fiscal, status='approved', approved_by=fin1,
        )
        ComplaintFeedback.objects.create(complaint=drain1, citizen=c1, rating=2,
            comment='Took 45 days for something that should have been a 2-day fix. Very disappointed.')
        self.stdout.write('  [OK] Scenario 2: Resolved with poor rating (drain cover, DSCC Water)')

        # ── 3. IN PROGRESS — active work ──────────────────────────────
        road2 = Complaint.objects.create(
            citizen=c2, title='Road completely dug up and left unfinished near Dhanmondi 27',
            description='Contractors dug up the road to lay cables but abandoned the site 3 weeks ago. '
                        'Half the road is impassable. No warning signs. Several accidents already.',
            category='roads', location_text='Road 27, Dhanmondi, DSCC',
            latitude=23.7497, longitude=90.3766,
            city_corp='DSCC', department=dscc_roads,
            status='in_progress', priority='critical',
            assigned_surveyor=sur1, assigned_worker=wrk2,
        )
        backdate(road2, 12)
        _log(road2, 'submitted', c2, 'Complaint submitted.')
        _log(road2, 'assigned', adm_dscc_roads, 'Assigned to surveyor.')
        _log(road2, 'budget_approved', fin1, 'Budget approved.')
        _log(road2, 'worker_assigned', adm_dscc_roads, 'Worker assigned.')
        _log(road2, 'in_progress', wrk2, 'Work started. Road surface being restored.')
        SurveyReport.objects.create(
            complaint=road2, surveyor=sur1,
            findings='60m stretch of road fully excavated. Needs backfill, compaction and re-tarmac.',
            labor_estimate=Decimal('120000'), equipment_estimate=Decimal('80000'),
            misc_estimate=Decimal('15000'), estimated_cost=Decimal('215000'),
            priority_recommendation='critical', estimated_days=7,
        )
        Expense.objects.create(
            title='Road restoration — Dhanmondi 27', department=dscc_roads,
            complaint=road2, amount=Decimal('215000'),
            fiscal_year=fiscal, status='approved', approved_by=fin2,
        )
        self.stdout.write('  [OK] Scenario 3: Critical road — in progress')

        # ── 4. BUDGET PENDING — waiting for finance ────────────────────
        elec1 = Complaint.objects.create(
            citizen=c3, title='Street lights not working for 2 weeks on Gulshan Avenue',
            description='The entire stretch of Gulshan Avenue from circle 1 to circle 2 has had no '
                        'street lights for two weeks. Robberies have increased. This is urgent.',
            category='electricity', location_text='Gulshan Avenue, Gulshan, DSCC',
            latitude=23.7925, longitude=90.4078,
            city_corp='DSCC', department=dscc_elec,
            status='budget_pending', priority='high',
            assigned_surveyor=sur2,
        )
        backdate(elec1, 8)
        _log(elec1, 'submitted', c3, 'Complaint submitted.')
        _log(elec1, 'assigned', adm_dscc_it, 'Assigned to surveyor.')
        _log(elec1, 'survey_done', sur2, 'Survey complete.')
        _log(elec1, 'budget_pending', sur2, 'Expense submitted. Awaiting finance approval.')
        SurveyReport.objects.create(
            complaint=elec1, surveyor=sur2,
            findings='Main distribution box faulty. 18 lamp posts affected. Box needs full replacement.',
            materials_needed='Distribution box unit, 18 LED lamp units, wiring.',
            labor_estimate=Decimal('45000'), equipment_estimate=Decimal('85000'),
            misc_estimate=Decimal('10000'), estimated_cost=Decimal('140000'),
            priority_recommendation='high', estimated_days=4,
        )
        Expense.objects.create(
            title='Street light repair — Gulshan Avenue', department=dscc_elec,
            complaint=elec1, amount=Decimal('140000'),
            fiscal_year=fiscal, status='pending',
        )
        _notify(fin1, 'Expense Pending Approval',
                f'Expense of BDT 1,40,000 pending for "{elec1.title}"', 'survey_done', elec1)
        _notify(fin2, 'Expense Pending Approval',
                f'Expense of BDT 1,40,000 pending for "{elec1.title}"', 'survey_done', elec1)
        self.stdout.write('  [OK] Scenario 4: Budget pending — street lights (DSCC Elec)')

        # ── 5. SURVEY IN PROGRESS ─────────────────────────────────────
        sanit1 = Complaint.objects.create(
            citizen=c4, title='Garbage not collected for 10 days in Lalbagh area',
            description='The garbage collection van has not visited our area for 10 consecutive days. '
                        'Waste is piling up on street corners. Health hazard. Smell is unbearable.',
            category='sanitation', location_text='Lalbagh Road, Old Dhaka, DSCC',
            city_corp='DSCC', department=dscc_sanit,
            status='surveying', priority='high',
            assigned_surveyor=sur5,
        )
        backdate(sanit1, 5)
        _log(sanit1, 'submitted', c4, 'Complaint submitted.')
        _log(sanit1, 'assigned', adm_dscc_sanit, f'Surveyor {sur5.get_full_name()} assigned.')
        _log(sanit1, 'surveying', sur5, 'Survey in progress. Visiting site today.')
        self.stdout.write('  [OK] Scenario 5: Survey in progress (sanitation)')

        # ── 6. UNDER REVIEW — newly received ──────────────────────────
        water1 = Complaint.objects.create(
            citizen=c5, title='Water supply completely cut off in Azimpur Colony',
            description='No water supply in Azimpur Colony since Monday morning. Around 200 families '
                        'are affected. The issue seems to be a burst main pipe near the main road.',
            category='water', location_text='Azimpur Colony, Lalbagh, DSCC',
            city_corp='DSCC', department=dscc_water,
            status='under_review', priority='critical',
        )
        backdate(water1, 2)
        _log(water1, 'submitted', c5, 'Complaint submitted.')
        _log(water1, 'under_review', adm_dscc_water, 'Logged and under review.')
        self.stdout.write('  [OK] Scenario 6: Under review — critical water supply outage')

        # ── 7. JUST SUBMITTED ─────────────────────────────────────────
        env1 = Complaint.objects.create(
            citizen=c6, title='Blocked storm drain causing severe flooding near Bashundhara',
            description='The storm drain on Bashundhara Ring Road is blocked with construction debris '
                        'and household waste. Every moderate rain floods the area knee-deep.',
            category='environment', location_text='Ring Road, Bashundhara, DSCC',
            city_corp='DSCC', department=dscc_env,
            status='submitted', priority='medium',
        )
        _log(env1, 'submitted', c6, 'Complaint submitted.')
        self.stdout.write('  [OK] Scenario 7: Just submitted (environment)')

        # ── 8. REJECTED — surveyor found it invalid ───────────────────
        fake1 = Complaint.objects.create(
            citizen=c7, title='Road in front of my shop needs painting not repair',
            description='The road in front of my shop looks old. I want the road to be repainted and '
                        'the markings refreshed. The road itself is fine.',
            category='roads', location_text='Malibagh Chowdhurypara, DSCC',
            city_corp='DSCC', department=dscc_roads,
            status='rejected', priority='low',
            assigned_surveyor=sur2,
        )
        backdate(fake1, 20)
        _log(fake1, 'submitted', c7, 'Complaint submitted.')
        _log(fake1, 'assigned', adm_dscc_roads, 'Assigned to surveyor for assessment.')
        _log(fake1, 'surveying', sur2, 'Survey started.')
        _log(fake1, 'rejected', sur2,
             'Surveyor rejected: Road is in good condition. Request is cosmetic — not within scope.')
        _notify(c7, 'Complaint Rejected',
                f'Your complaint "{fake1.title}" was assessed and rejected. '
                'Road surface is in satisfactory condition.', 'general', fake1)
        self.stdout.write('  [OK] Scenario 8: Rejected — cosmetic complaint')

        # ── 9. REJECTED BUDGET — too expensive ────────────────────────
        fancy1 = Complaint.objects.create(
            citizen=c8, title='Entire Panthapath footpath cracked and needs replacement',
            description='The footpath along the entire Panthapath stretch is badly cracked. '
                        'People are tripping. Needs full reconstruction with tiles.',
            category='roads', location_text='Panthapath, Karwan Bazar, DSCC',
            city_corp='DSCC', department=dscc_roads,
            status='rejected', priority='medium',
            assigned_surveyor=sur1,
        )
        backdate(fancy1, 25)
        _log(fancy1, 'submitted', c8, 'Complaint submitted.')
        _log(fancy1, 'assigned', adm_dscc_roads, 'Assigned to surveyor.')
        _log(fancy1, 'survey_done', sur1, 'Survey complete.')
        _log(fancy1, 'budget_pending', sur1, 'Expense submitted — very large estimate.')
        _log(fancy1, 'rejected', fin2,
             'Budget rejected: Estimate of BDT 18,00,000 exceeds allocated budget for this quarter. '
             'Recommend phased approach or budget revision.')
        SurveyReport.objects.create(
            complaint=fancy1, surveyor=sur1,
            findings='Full footpath 400m long. Extensive cracking throughout. Full tile replacement needed.',
            materials_needed='Interlocking tiles 4000 pcs, sand, cement, kerb stones.',
            labor_estimate=Decimal('600000'), equipment_estimate=Decimal('900000'),
            misc_estimate=Decimal('300000'), estimated_cost=Decimal('1800000'),
            priority_recommendation='medium', estimated_days=30,
        )
        Expense.objects.create(
            title='Footpath reconstruction — Panthapath', department=dscc_roads,
            complaint=fancy1, amount=Decimal('1800000'),
            fiscal_year=fiscal, status='rejected', approved_by=fin2,
            rejection_reason='Estimate exceeds quarterly budget. Phased approach recommended.',
        )
        _notify(c8, 'Budget Rejected',
                f'Budget for your complaint "{fancy1.title}" was rejected due to insufficient funds.',
                'budget_rejected', fancy1)
        self.stdout.write('  [OK] Scenario 9: Budget rejected — over budget estimate')

        # ── 10. ANONYMOUS COMPLAINT ────────────────────────────────────
        anon1 = Complaint.objects.create(
            citizen=c9, title='Corrupt contractor doing substandard road work on Moghbazar',
            description='The contractor hired by the corporation is using substandard materials on '
                        'Moghbazar road. Sand is mixed with too much water. Work will fail in weeks.',
            category='roads', location_text='Moghbazar, Ramna, DSCC',
            city_corp='DSCC', department=dscc_roads,
            status='under_review', priority='high', is_anonymous=True,
        )
        backdate(anon1, 3)
        _log(anon1, 'submitted', c9, 'Anonymous complaint submitted.')
        _log(anon1, 'under_review', adm_dscc_roads, 'Under review.')
        self.stdout.write('  [OK] Scenario 10: Anonymous complaint (contractor corruption)')

        # ── 11. DUPLICATE COMPLAINT — same area, same category ────────
        dup_primary = Complaint.objects.create(
            citizen=c10, title='Giant pothole near Science Lab School, Dhanmondi',
            description='A massive pothole has appeared on road 8A in Dhanmondi near Science Lab School. '
                        'Two motorcycles have already had accidents.',
            category='roads', location_text='Road 8A, Dhanmondi, DSCC',
            latitude=23.7452, longitude=90.3736,
            city_corp='DSCC', department=dscc_roads,
            status='assigned', priority='high', assigned_surveyor=sur1,
        )
        backdate(dup_primary, 6)

        dup_secondary = Complaint.objects.create(
            citizen=c11, title='Big hole in road near Dhanmondi Lake Road 8',
            description='There is a huge hole in the road near Dhanmondi lake side. Very dangerous at night.',
            category='roads', location_text='Lake Road 8, Dhanmondi, DSCC',
            latitude=23.7455, longitude=90.3740,  # within 500m of dup_primary
            city_corp='DSCC', department=dscc_roads,
            status='submitted', priority='medium',
            is_duplicate=True, duplicate_of=dup_primary,
        )
        backdate(dup_secondary, 5)
        dup_primary.co_reporters.add(c11)
        _log(dup_primary, 'submitted', c10, 'Complaint submitted.')
        _log(dup_primary, 'assigned', adm_dscc_roads, 'Assigned to surveyor.')
        _log(dup_secondary, 'submitted', c11, 'Complaint submitted.')
        _log(dup_secondary, 'submitted', None,
             f'Auto-detected as duplicate of #{dup_primary.pk}.', 'merged_as_duplicate')
        _log(dup_primary, 'assigned', None,
             f'Complaint #{dup_secondary.pk} merged as co-report.', 'merged_as_primary')
        _notify(c11, 'Similar Report Found',
                f'Your complaint is similar to an existing report. You have been added as co-reporter.',
                'complaint_merged', dup_primary)
        self.stdout.write('  [OK] Scenario 11: Duplicate complaint detected and merged')

        # ── 12. TRANSFER REQUEST — wrong department ────────────────────
        wrong_dept = Complaint.objects.create(
            citizen=c12, title='Illegal building construction blocking public pathway',
            description='Neighbours are illegally extending their building into the public pathway '
                        'in our colony. This is blocking access for emergency vehicles.',
            category='building', location_text='Shantinagar, Motijheel, DSCC',
            city_corp='DSCC', department=dscc_roads,  # sent to roads by mistake
            status='under_review', priority='medium',
        )
        backdate(wrong_dept, 10)
        _log(wrong_dept, 'submitted', c12, 'Complaint submitted.')
        _log(wrong_dept, 'under_review', adm_dscc_roads, 'Received — this is a building issue, not roads.')

        building_dept = self._dept('building', 'DSCC')
        if building_dept:
            tr = ComplaintTransferRequest.objects.create(
                complaint=wrong_dept,
                from_department=dscc_roads,
                to_department=building_dept,
                reason='This complaint relates to illegal construction, which falls under the '
                       'Building & Construction Department. Requesting transfer.',
                status='pending',
                requested_by=adm_dscc_roads,
            )
            _log(wrong_dept, 'under_review', adm_dscc_roads,
                 f'Transfer requested to {building_dept.name}.', 'transfer_requested')
            _notify(sa, 'Transfer Request',
                    f'Admin requests transfer of "{wrong_dept.title}" to Building Dept.',
                    'transfer_requested', wrong_dept)
            self.stdout.write('  [OK] Scenario 12: Transfer request pending (wrong dept routing)')
        else:
            self.stdout.write('  ! Scenario 12 skipped — building dept not found')

        # ── 13. APPROVED TRANSFER ──────────────────────────────────────
        it_complaint = Complaint.objects.create(
            citizen=c13, title='CCTV cameras in Gulshan malfunctioning for 3 months',
            description='The CCTV cameras installed by the corporation in Gulshan Circle 1 have been '
                        'offline for 3 months. Security has deteriorated. The cameras need repair.',
            category='it', location_text='Gulshan Circle 1, DSCC',
            city_corp='DSCC', department=dscc_water,  # initially mis-routed to water
            status='assigned', priority='high',
            assigned_surveyor=sur2,
        )
        backdate(it_complaint, 15)
        _log(it_complaint, 'submitted', c13, 'Complaint submitted.')
        _log(it_complaint, 'under_review', adm_dscc_water, 'Received. This belongs to IT department.')

        # scenario 13 transfer is always created (water → IT, no building dependency)
        ComplaintTransferRequest.objects.create(
            complaint=it_complaint,
            from_department=dscc_water,
            to_department=dscc_it,
            reason='CCTV is IT infrastructure — transfer to DSCC IT department.',
            status='approved',
            requested_by=adm_dscc_water,
            reviewed_by=sa,
        )
        it_complaint.department = dscc_it
        it_complaint.save(update_fields=['department', 'updated_at'])
        _log(it_complaint, it_complaint.status, sa,
             f'Transfer from {dscc_water.name} to {dscc_it.name} approved.', 'transfer_approved')
        _notify(adm_dscc_it, 'Complaint Transferred',
                f'"{it_complaint.title}" has been transferred to your department.',
                'transfer_approved', it_complaint)
        self.stdout.write('  [OK] Scenario 13: Transfer approved — IT complaint moved from Water to IT')

        # ── 14. RESURVEY REQUESTED — worker found bigger problem ───────
        resurvey1 = Complaint.objects.create(
            citizen=c14, title='Cracked water pipe leaking in Wari area',
            description='A water pipe under the road has cracked and is leaking, causing a sinkhole '
                        'to form. The leak has been there for 2 weeks and is getting worse.',
            category='water', location_text='Wari, Old Dhaka, DSCC',
            city_corp='DSCC', department=dscc_water,
            status='under_review', priority='critical',
        )
        backdate(resurvey1, 18)
        _log(resurvey1, 'submitted', c14, 'Complaint submitted.')
        _log(resurvey1, 'assigned', adm_dscc_water, 'Assigned surveyor.')
        _log(resurvey1, 'survey_done', sur3, 'Survey done — pipe crack assessed.')
        SurveyReport.objects.create(
            complaint=resurvey1, surveyor=sur3,
            findings='1.5 inch surface crack in supply pipe. Expected: simple patch.',
            labor_estimate=Decimal('15000'), equipment_estimate=Decimal('20000'),
            misc_estimate=Decimal('3000'), estimated_cost=Decimal('38000'),
            priority_recommendation='critical', estimated_days=2,
        )
        _log(resurvey1, 'budget_approved', fin1, 'Budget approved.')
        _log(resurvey1, 'worker_assigned', adm_dscc_water, 'Worker assigned.')
        _log(resurvey1, 'under_review', wrk3,
             'Resurvey requested: Found full pipe section collapsed, not just a crack. '
             'Needs 40m pipe replacement, not a patch. Original estimate was too low.', 'status_change')
        _notify(adm_dscc_water, 'Resurvey Requested',
                f'Worker found larger issue in "{resurvey1.title}". Resurvey needed.',
                'general', resurvey1)
        self.stdout.write('  [OK] Scenario 14: Resurvey requested — problem bigger than estimated')

        # ── 15. WORKER ASSIGNED — waiting to start ────────────────────
        sanit2 = Complaint.objects.create(
            citizen=c15, title='Manhole cover missing near Shaheed Minar, causing injury risk',
            description='The manhole cover near Shaheed Minar central road is completely missing. '
                        'A child nearly fell in yesterday. Must be covered immediately.',
            category='sanitation', location_text='Shaheed Minar, Dhaka University, DSCC',
            city_corp='DSCC', department=dscc_sanit,
            status='worker_assigned', priority='critical',
            assigned_surveyor=sur5, assigned_worker=wrk4,
        )
        backdate(sanit2, 4)
        _log(sanit2, 'submitted', c15, 'Complaint submitted.')
        _log(sanit2, 'assigned', adm_dscc_sanit, 'Assigned to surveyor.')
        _log(sanit2, 'budget_approved', fin2, 'Budget approved.')
        _log(sanit2, 'worker_assigned', adm_dscc_sanit, f'Assigned to {wrk4.get_full_name()}.')
        SurveyReport.objects.create(
            complaint=sanit2, surveyor=sur5,
            findings='Manhole cover missing. Cast iron replacement required. Safety cone placed.',
            labor_estimate=Decimal('3000'), equipment_estimate=Decimal('8000'),
            misc_estimate=Decimal('500'), estimated_cost=Decimal('11500'),
            priority_recommendation='critical', estimated_days=1,
        )
        Expense.objects.create(
            title='Manhole cover replacement — Shaheed Minar', department=dscc_sanit,
            complaint=sanit2, amount=Decimal('11500'),
            fiscal_year=fiscal, status='approved', approved_by=fin2,
        )
        self.stdout.write('  [OK] Scenario 15: Worker assigned — critical manhole cover')

        # ── 16. ESCALATED / OVERDUE — submitted 3 months ago ──────────
        overdue1 = Complaint.objects.create(
            citizen=c16, title='Collapsed retaining wall on Khilgaon Circular Road — dangerous',
            description='A retaining wall on the Khilgaon Circular Road collapsed 3 months ago. '
                        'No action taken. Soil is now eroding onto the road during rain.',
            category='roads', location_text='Khilgaon Circular Road, Khilgaon, DSCC',
            city_corp='DSCC', department=dscc_roads,
            status='under_review', priority='critical',
        )
        backdate(overdue1, 92)
        _log(overdue1, 'submitted', c16, 'Complaint submitted.')
        _log(overdue1, 'under_review', adm_dscc_roads, 'Under review.')
        self.stdout.write('  [OK] Scenario 16: Overdue complaint (92 days, no action)')

        # ── 17. COMPLAINT WITHOUT GPS ──────────────────────────────────
        no_gps = Complaint.objects.create(
            citizen=c17, title='Speed bumps removed without notice on Tejgaon link road',
            description='The speed bumps that were recently installed on Tejgaon Link Road have been '
                        'removed. Vehicles are now speeding. Multiple near misses reported.',
            category='roads', location_text='Tejgaon Link Road, Tejgaon, DSCC',
            # no latitude/longitude
            city_corp='DSCC', department=dscc_roads,
            status='submitted', priority='medium',
        )
        _log(no_gps, 'submitted', c17, 'Complaint submitted (no GPS coordinates).')
        self.stdout.write('  [OK] Scenario 17: Complaint submitted without GPS')

        # ── 18. DNCC COMPLAINT — different corp ────────────────────────
        dncc1 = Complaint.objects.create(
            citizen=c18, title='Footpath encroached by hawkers near Agargaon colony',
            description='Unlicensed hawkers have fully occupied the footpath near Agargaon colony. '
                        'Pedestrians are forced to walk on the road. Very unsafe.',
            category='roads', location_text='Agargaon Colony Road, Agargaon, DNCC',
            latitude=23.7780, longitude=90.3686,
            city_corp='DNCC', department=dncc_roads,
            status='assigned', priority='medium', assigned_surveyor=sur4,
        )
        backdate(dncc1, 7)
        _log(dncc1, 'submitted', c18, 'Complaint submitted.')
        _log(dncc1, 'under_review', adm_dncc_roads, 'Under review.')
        _log(dncc1, 'assigned', adm_dncc_roads, f'Assigned to {sur4.get_full_name()}.')
        self.stdout.write('  [OK] Scenario 18: DNCC complaint (different corp) — assigned')

        # ── 19. CLOSED — resolved and closed ──────────────────────────
        closed1 = Complaint.objects.create(
            citizen=c19, title='Broken park bench in Dhanmondi Lake Park',
            description='Multiple benches in Dhanmondi Lake Park are broken, with sharp metal edges '
                        'protruding. Children have been injured.',
            category='parks', location_text='Dhanmondi Lake Park, Dhanmondi, DSCC',
            city_corp='DSCC', status='closed', priority='low',
        )
        backdate(closed1, 60)
        _log(closed1, 'submitted', c19, 'Complaint submitted.')
        _log(closed1, 'resolved', adm_dscc_roads, 'Benches repaired by contractor.')
        _log(closed1, 'closed', adm_dscc_roads, 'Complaint closed after 14-day cooling period.')
        ComplaintFeedback.objects.create(complaint=closed1, citizen=c19, rating=5,
            comment='Excellent! The benches were fixed within a week.')
        self.stdout.write('  [OK] Scenario 19: Closed complaint with 5-star feedback')

        # ── 20. MULTIPLE COMPLAINTS SAME AREA ─────────────────────────
        for i, (cit, title, cat, loc) in enumerate([
            (c0, 'Waterlogging in Mirpur 10 after every rain', 'water',
             'Mirpur 10, Mirpur, DSCC'),
            (c1, 'Illegal dumping of waste near Mirpur 10 bus stand', 'sanitation',
             'Mirpur 10 Bus Stand, DSCC'),
            (c2, 'Street light broken outside Mirpur 10 metro station', 'electricity',
             'Mirpur 10 Metro Station, DSCC'),
        ]):
            c_new = Complaint.objects.create(
                citizen=cit, title=title, category=cat,
                description=f'Ongoing issue reported by citizen. Requires immediate attention. '
                            f'This has been a persistent problem in the {loc} area.',
                location_text=loc, city_corp='DSCC',
                status='submitted', priority='medium',
                department=dscc_water if cat == 'water' else (
                    dscc_sanit if cat == 'sanitation' else dscc_elec),
            )
            _log(c_new, 'submitted', cit, 'Complaint submitted.')
        self.stdout.write('  [OK] Scenario 20: Multiple complaints in same area (Mirpur 10)')

        # ── 21. PERMISSION ABUSE ATTEMPT ──────────────────────────────
        # (simulated via log notes — actual enforcement is in views)
        abuse_log = Complaint.objects.create(
            citizen=c5, title='Test: Admin tried to view another corp complaint',
            description='Test scenario: Admin from DSCC Roads attempted to view a DNCC complaint. '
                        'System correctly denied access. No data breach.',
            category='admin_dept', location_text='System test, DSCC',
            city_corp='DSCC', department=dscc_roads,
            status='closed', priority='low',
        )
        _log(abuse_log, 'submitted', c5, 'Permission test complaint submitted.')
        _log(abuse_log, 'closed', adm_dscc_roads, 'Access control verified. Closed as test.')
        self.stdout.write('  [OK] Scenario 21: Permission abuse attempt (logged, access denied)')

        # ── 22. SURVEY REVISION — second survey submitted ──────────────
        resurvey2 = Complaint.objects.create(
            citizen=c6, title='IT fibre cable hanging dangerously low on Banani Road 11',
            description='A fibre optic cable is hanging very low across Banani Road 11. '
                        'Tall vehicles are catching it. Risk of cable snap and injury.',
            category='it', location_text='Road 11, Banani, DSCC',
            city_corp='DSCC', department=dscc_it,
            status='budget_pending', priority='high',
            assigned_surveyor=tech1,
        )
        backdate(resurvey2, 9)
        # first survey (under-estimated)
        first_sr = SurveyReport.objects.create(
            complaint=resurvey2, surveyor=sur2,
            findings='Cable sagging 3m. Needs re-tensioning and pole anchor.',
            labor_estimate=Decimal('5000'), equipment_estimate=Decimal('3000'),
            misc_estimate=Decimal('500'), estimated_cost=Decimal('8500'),
            priority_recommendation='medium', estimated_days=1,
        )
        # second survey (revised, more complete) — update_or_create overwrites
        SurveyReport.objects.filter(complaint=resurvey2).update(
            findings='Cable sagging 3m but pole itself is tilting. Full pole replacement + cable re-routing needed.',
            labor_estimate=Decimal('22000'), equipment_estimate=Decimal('35000'),
            misc_estimate=Decimal('5000'), estimated_cost=Decimal('62000'),
            priority_recommendation='high', estimated_days=3,
        )
        Expense.objects.create(
            title='Fibre cable + pole repair — Banani Road 11', department=dscc_it,
            complaint=resurvey2, amount=Decimal('62000'),
            fiscal_year=fiscal, status='pending',
        )
        _log(resurvey2, 'submitted', c6, 'Complaint submitted.')
        _log(resurvey2, 'survey_done', sur2, 'Initial survey done — estimate BDT 8,500.')
        _log(resurvey2, 'survey_done', sur2, 'Survey revised — pole tilting found. New estimate BDT 62,000.')
        _log(resurvey2, 'budget_pending', sur2, 'Revised expense submitted for approval.')
        self.stdout.write('  [OK] Scenario 22: Survey revision — estimate updated (update_or_create)')

        # ── 23. CONCURRENT INTERACTION — 2 citizens file same issue ───
        same1 = Complaint.objects.create(
            citizen=c7, title='Raw sewage overflowing from drain on Fakirapool street',
            description='Drain near Fakirapool fish market is overflowing with raw sewage. '
                        'Market is flooded. Health risk for vendors and customers.',
            category='water', location_text='Fakirapool Market, Motijheel, DSCC',
            latitude=23.7285, longitude=90.4204,
            city_corp='DSCC', department=dscc_water,
            status='assigned', priority='critical', assigned_surveyor=sur3,
        )
        same2 = Complaint.objects.create(
            citizen=c8, title='Sewage flooding at Fakirapool — very bad smell',
            description='The entire Fakirapool area smells of sewage. Drain is overflowing. '
                        'Many people are sick. Filed separate complaint as I did not see the first one.',
            category='water', location_text='Fakirapool, Motijheel, DSCC',
            latitude=23.7288, longitude=90.4207,
            city_corp='DSCC', department=dscc_water,
            status='submitted', priority='critical',
            is_duplicate=True, duplicate_of=same1,
        )
        same1.co_reporters.add(c8)
        _log(same1, 'submitted', c7, 'Complaint submitted.')
        _log(same1, 'assigned', adm_dscc_water, 'Assigned as critical priority.')
        _log(same2, 'submitted', c8, 'Complaint submitted.')
        _log(same2, 'submitted', None,
             f'Auto-merged as duplicate of #{same1.pk} — same location & category.', 'merged_as_duplicate')
        self.stdout.write('  [OK] Scenario 23: Concurrent same-issue complaints — auto-merged')

        # ── 24. EXTRA NOTIFS for realism ──────────────────────────────
        for cit in citizens[:5]:
            _notify(cit, 'Welcome to CivicEye',
                    'Your account is now active. Report issues in your area and track them in real time.',
                    'general')

        self.stdout.write(self.style.SUCCESS('\n=== Demo Data Complete ==='))
        self.stdout.write('\n--- ACCOUNT REFERENCE ---')
        self.stdout.write('Role             Username              Password')
        self.stdout.write('-' * 55)
        self.stdout.write('Super Admin      SSNSTCE               SSNSTCE')
        self.stdout.write('Finance Officer  mehedi_finance        Finance@2026')
        self.stdout.write('Finance Officer  nasrin_finance        Finance@2026')
        self.stdout.write('Dept Admin*Head  rafiq_admin           Admin@2026   (DSCC Roads)')
        self.stdout.write('Dept Admin*Head  taslima_admin         Admin@2026   (DSCC IT)')
        self.stdout.write('Dept Admin*Head  shabana_admin         Admin@2026   (DSCC Water)')
        self.stdout.write('Dept Admin       karim_admin           Admin@2026   (DNCC Roads)')
        self.stdout.write('Dept Admin       reza_admin            Admin@2026   (DSCC Sanit)')
        self.stdout.write('Surveyor         labib_surveyor        Survey@2026  (DSCC Roads)')
        self.stdout.write('Surveyor         sadia_surveyor        Survey@2026  (DSCC Roads)')
        self.stdout.write('Surveyor         tamim_surveyor        Survey@2026  (DSCC Water)')
        self.stdout.write('Surveyor         mitu_surveyor         Survey@2026  (DNCC Roads)')
        self.stdout.write('Surveyor         jahid_surveyor        Survey@2026  (DSCC Sanit)')
        self.stdout.write('Field Worker     lamiya_worker         Worker@2026  (DSCC Roads)')
        self.stdout.write('Field Worker     arif_worker           Worker@2026  (DSCC Roads)')
        self.stdout.write('Field Worker     rokon_worker          Worker@2026  (DSCC Water)')
        self.stdout.write('Field Worker     sharmin_worker        Worker@2026  (DSCC Sanit)')
        self.stdout.write('Field Worker     mosharraf_worker      Worker@2026  (DNCC Roads)')
        self.stdout.write('Technician       sujan_tech            Tech@2026    (DSCC IT)')
        self.stdout.write('Technician       farida_tech           Tech@2026    (DSCC IT)')
        self.stdout.write('Technician       ripon_tech            Tech@2026    (DSCC Elec)')
        self.stdout.write('Technician       shirin_tech           Tech@2026    (DSCC Elec)')
        self.stdout.write('Technician       imran_tech            Tech@2026    (DSCC IT)')
        self.stdout.write('Citizen (×20)    rahim_citizen …       Citi@2026')
        self.stdout.write('\n* = Department Head flag set')
        self.stdout.write(f'\nTotal complaints created: {Complaint.objects.count()}')
        self.stdout.write(f'Total users: {User.objects.count()}')
        self.stdout.write(f'Total survey reports: {SurveyReport.objects.count()}')
        self.stdout.write(f'Total expenses: {Expense.objects.count()}')
        self.stdout.write(f'Transfer requests: {ComplaintTransferRequest.objects.count()}')
        self.stdout.write(f'Feedback records: {ComplaintFeedback.objects.count()}')
