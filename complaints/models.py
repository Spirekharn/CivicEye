from django.db import models
from django.conf import settings


CATEGORY_CHOICES = [
    ('roads',       'Roads & Infrastructure'),
    ('water',       'Water & Sewerage'),
    ('electricity', 'Electricity & Street Lights'),
    ('sanitation',  'Sanitation & Waste'),
    ('parks',       'Parks & Recreation'),
    ('health',      'Public Health'),
    ('building',    'Building & Construction'),
    ('transport',   'Transport & Traffic'),
    ('environment', 'Environment & Drainage'),
    ('fire',        'Fire & Emergency'),
    ('it',          'IT & Technology'),
    ('admin_dept',  'General Administration'),
    ('other',       'Other'),
]

STATUS_CHOICES = [
    ('submitted',       'Submitted'),
    ('under_review',    'Under Review'),
    ('assigned',        'Assigned to Surveyor'),
    ('surveying',       'Survey in Progress'),
    ('survey_done',     'Survey Complete'),
    ('budget_pending',  'Budget Pending'),
    ('budget_approved', 'Budget Approved'),
    ('worker_assigned', 'Worker Assigned'),
    ('in_progress',     'Work in Progress'),
    ('resolved',        'Resolved'),
    ('closed',          'Closed'),
    ('rejected',        'Rejected'),
]

PRIORITY_CHOICES = [
    ('low',      'Low'),
    ('medium',   'Medium'),
    ('high',     'High'),
    ('critical', 'Critical'),
]

# Progress percentage per status (for the progress bar)
STATUS_PROGRESS = {
    'submitted': 8, 'under_review': 16, 'assigned': 24,
    'surveying': 32, 'survey_done': 42, 'budget_pending': 52,
    'budget_approved': 62, 'worker_assigned': 72,
    'in_progress': 82, 'resolved': 100, 'closed': 100, 'rejected': 0,
}


class Complaint(models.Model):
    STATUS_CHOICES  = STATUS_CHOICES
    PRIORITY_CHOICES= PRIORITY_CHOICES

    title       = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Who filed it and where it belongs
    citizen     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    department  = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL, related_name='complaints')
    city_corp   = models.CharField(max_length=10, blank=True)  # auto-filled from location

    # Location
    location_text = models.CharField(max_length=300)
    latitude      = models.FloatField(null=True, blank=True)
    longitude     = models.FloatField(null=True, blank=True)

    # Staff assignments
    assigned_surveyor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='survey_assignments')
    assigned_worker   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='work_assignments')

    # Media evidence
    image = models.ImageField(upload_to='complaints/images/', null=True, blank=True)
    completion_image = models.ImageField(upload_to='complaints/completion/', null=True, blank=True)

    # Flags
    is_anonymous = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    duplicate_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} {self.title}"

    def get_status_progress(self):
        return STATUS_PROGRESS.get(self.status, 0)

    def required_worker_type(self):
        from departments.models import CATEGORY_WORKER_TYPE
        return CATEGORY_WORKER_TYPE.get(self.category, 'worker')


class ComplaintStatusHistory(models.Model):
    complaint  = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes      = models.TextField(blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class SurveyReport(models.Model):
    complaint           = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='survey_report')
    surveyor            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    findings            = models.TextField()
    materials_needed    = models.TextField(blank=True)
    labor_estimate      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    equipment_estimate  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    misc_estimate       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estimated_cost      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    priority_recommendation = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    estimated_days      = models.PositiveIntegerField(default=7)
    survey_image        = models.ImageField(upload_to='complaints/surveys/', null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)


class ComplaintFeedback(models.Model):
    complaint  = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    citizen    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating     = models.PositiveSmallIntegerField(default=3)
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
