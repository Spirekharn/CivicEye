from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from complaints.models import Complaint

class SurveyReport(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)

    surveyor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    report = models.TextField()

    estimated_cost = models.FloatField()

    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey for {self.complaint.title}"