from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('complaint_submitted', 'Complaint Submitted'),
        ('complaint_assigned',  'Complaint Assigned'),
        ('survey_request',      'Survey Requested'),
        ('survey_done',         'Survey Completed'),
        ('budget_approved',     'Budget Approved'),
        ('budget_rejected',     'Budget Rejected'),
        ('worker_assigned',     'Worker Assigned'),
        ('complaint_resolved',  'Complaint Resolved'),
        ('duplicate_found',     'Duplicate Detected'),
        ('general',             'General'),
    ]
    user              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title             = models.CharField(max_length=200)
    message           = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    complaint         = models.ForeignKey('complaints.Complaint', null=True, blank=True, on_delete=models.SET_NULL)
    is_read           = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"
