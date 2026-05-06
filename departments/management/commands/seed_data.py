"""
departments/management/commands/seed_data.py
Run with: python manage.py seed_data
Creates departments for each city corporation + test accounts.
"""
from django.core.management.base import BaseCommand
from departments.models import Department
from accounts.models import User
from finance.models import DepartmentBudget


DEPT_TEMPLATE = [
    ('roads',       'Roads & Infrastructure',       4000000),
    ('water',       'Water & Sewerage',              3500000),
    ('electricity', 'Electricity & Street Lights',  3000000),
    ('sanitation',  'Sanitation & Waste',            2500000),
    ('environment', 'Environment & Drainage',        2000000),
    ('fire',        'Fire & Emergency',              3000000),
    ('it',          'IT & Technology',               1500000),
    ('transport',   'Transport & Traffic',           2000000),
]

CORPS = [
    ('DNCC', 'Dhaka North'),
    ('DSCC', 'Dhaka South'),
    ('CCC',  'Chattogram'),
    ('KCC',  'Khulna'),
    ('RCC',  'Rajshahi'),
    ('BCC',  'Barishal'),
    ('SCC',  'Sylhet'),
    ('MCC',  'Mymensingh'),
    ('GCC',  'Gazipur'),
    ('NCC',  'Narayanganj'),
    ('COCC', 'Cumilla'),
    ('RNCC', 'Rangpur'),
]


class Command(BaseCommand):
    help = 'Seeds departments and test users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding departments...')
        depts_created = {}

        for corp, corp_label in CORPS:
            for slug, name, budget in DEPT_TEMPLATE:
                dept, created = Department.objects.get_or_create(
                    slug=slug, city_corp=corp,
                    defaults={'name': f'{name}', 'is_active': True}
                )
                if created:
                    self.stdout.write(f'  + {corp}: {name}')
                depts_created[f'{corp}_{slug}'] = dept

        # Create/update the project super admin used for local demos.
        su, created = User.objects.get_or_create(username='SSNSTCE')
        su.email = su.email or 'ssnstce@civiceye.bd'
        su.role = 'super_admin'
        su.is_staff = True
        su.is_superuser = True
        su.first_name = su.first_name or 'Super'
        su.last_name = su.last_name or 'Admin'
        su.set_password('SSNSTCE')
        su.save()
        self.stdout.write(f'  {"Created" if created else "Updated"} SSNSTCE super admin')

        # Department admin for DSCC Roads
        dscc_roads = depts_created.get('DSCC_roads')
        dscc_it = depts_created.get('DSCC_it')
        if dscc_roads and not User.objects.filter(username='admin_dscc').exists():
            u = User.objects.create_user('admin_dscc', 'admin.dscc@civiceye.bd', 'Admin@123',
                first_name='DSCC', last_name='Admin', role='admin', department=dscc_roads)
            self.stdout.write(f'  Created admin_dscc -> {dscc_roads}')

        # Finance officer (no department)
        finance_user, created = User.objects.get_or_create(username='finance_officer')
        finance_user.role = 'finance'
        finance_user.department = None
        finance_user.first_name = finance_user.first_name or 'Finance'
        finance_user.last_name = finance_user.last_name or 'Officer'
        finance_user.is_active = True
        finance_user.set_password('Finance@123')
        finance_user.save()
        self.stdout.write(f'  {"Created" if created else "Updated"} finance_officer')

        demo_users = [
            ('Swagoto', '23101124', 'citizen', None, 'Swagoto', ''),
            ('qq', '123456', 'citizen', None, 'Citizen', ''),
            ('Sujan', '23101120', 'technician', dscc_it, 'Sujan', ''),
            ('Labib', '23101128', 'surveyor', dscc_roads, 'Labib', ''),
            ('Lamiya', '23101132', 'worker', dscc_roads, 'Lamiya', ''),
        ]
        for username, password, role, dept, first_name, last_name in demo_users:
            user, created = User.objects.get_or_create(username=username)
            user.role = role
            user.department = dept
            user.first_name = user.first_name or first_name
            user.last_name = user.last_name or last_name
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(f'  {"Created" if created else "Updated"} {username}')

        # Seed budgets for all created depts
        sa = User.objects.filter(role='super_admin').first()
        for dept in Department.objects.filter(is_active=True):
            match = next((b for s,n,b in DEPT_TEMPLATE if s == dept.slug), 2000000)
            DepartmentBudget.objects.get_or_create(
                department=dept, fiscal_year='2025-2026',
                defaults={'allocated_amount': match, 'allocated_by': sa}
            )

        self.stdout.write(self.style.SUCCESS('\nSeed complete! Test accounts:'))
        self.stdout.write('  SSNSTCE / SSNSTCE         (Super Admin)')
        self.stdout.write('  finance_officer / Finance@123 (Finance Officer)')
        self.stdout.write('  admin_dscc / Admin@123    (Dept Admin, DSCC Roads)')
        self.stdout.write('  Swagoto / 23101124        (Citizen)')
        self.stdout.write('  qq / 123456               (Citizen)')
        self.stdout.write('  Sujan / 23101120          (Technician)')
        self.stdout.write('  Labib / 23101128          (Surveyor)')
        self.stdout.write('  Lamiya / 23101132         (Field Worker)')
        self.stdout.write(f'\n  Departments seeded for all 12 city corporations.')
