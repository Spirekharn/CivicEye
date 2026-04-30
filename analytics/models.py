from django.db import models

# Create your models here.
from django.db import models
from complaints.models import Complaint


class DuplicateComplaint(models.Model):
    original = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='original_complaint'
    )

    duplicate = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='duplicate_complaint'
    )

    similarity_score = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Duplicate: {self.original.id} -> {self.duplicate.id}"