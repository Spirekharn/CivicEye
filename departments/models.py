from django.db import models


CITY_CORP_CHOICES = [
    ('DNCC', 'Dhaka North City Corporation'),
    ('DSCC', 'Dhaka South City Corporation'),
    ('CCC',  'Chattogram City Corporation'),
    ('SCC',  'Sylhet City Corporation'),
    ('RCC',  'Rajshahi City Corporation'),
    ('KCC',  'Khulna City Corporation'),
    ('BCC',  'Barishal City Corporation'),
    ('NCC',  'Narayanganj City Corporation'),
    ('GCC',  'Gazipur City Corporation'),
    ('MCC',  'Mymensingh City Corporation'),
]

SLUG_CHOICES = [
    ('roads',        'Roads & Infrastructure'),
    ('water',        'Water & Sewerage'),
    ('electricity',  'Electricity & Street Lights'),
    ('sanitation',   'Sanitation & Waste'),
    ('parks',        'Parks & Recreation'),
    ('health',       'Public Health'),
    ('building',     'Building & Construction'),
    ('transport',    'Transport & Traffic'),
    ('environment',  'Environment & Drainage'),
    ('fire',         'Fire & Emergency'),
    ('it',           'IT & Technology'),
    ('admin_dept',   'General Administration'),
]

# Maps physical categories to worker type
# 'worker' = field/labour, 'technician' = tech specialist
CATEGORY_WORKER_TYPE = {
    'roads':       'worker',
    'water':       'worker',
    'sanitation':  'worker',
    'parks':       'worker',
    'building':    'worker',
    'environment': 'worker',
    'fire':        'worker',
    'health':      'worker',
    'electricity': 'technician',
    'transport':   'technician',
    'it':          'technician',
    'admin_dept':  'worker',
}


class Department(models.Model):
    name         = models.CharField(max_length=100)
    slug         = models.CharField(max_length=30, choices=SLUG_CHOICES)
    city_corp    = models.CharField(max_length=10, choices=CITY_CORP_CHOICES, default='DSCC')
    description  = models.TextField(blank=True)
    contact_email= models.EmailField(blank=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['city_corp', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_city_corp_display()})"

    @property
    def total_budget(self):
        b = self.budgets.filter(fiscal_year='2025-2026').first()
        return b.allocated_amount if b else 0

    @property
    def spent_budget(self):
        from finance.models import Expense
        from django.db.models import Sum
        total = Expense.objects.filter(
            department=self, fiscal_year='2025-2026', status='approved'
        ).aggregate(Sum('amount'))['amount__sum']
        return total or 0

    @property
    def remaining_budget(self):
        return self.total_budget - self.spent_budget
