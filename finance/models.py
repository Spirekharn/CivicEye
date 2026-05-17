from datetime import date
from django.db import models
from django.conf import settings


def get_fiscal_year():
    today = date.today()
    if today.month >= 7:
        return f'{today.year}-{today.year + 1}'
    return f'{today.year - 1}-{today.year}'


class DepartmentBudget(models.Model):
    department     = models.ForeignKey('departments.Department', on_delete=models.CASCADE, related_name='budgets')
    fiscal_year    = models.CharField(max_length=9, default=get_fiscal_year)
    allocated_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    allocated_by   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['department', 'fiscal_year']

    def __str__(self):
        return f"{self.department.name} – {self.fiscal_year}: ৳{self.allocated_amount}"


class Expense(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    title         = models.CharField(max_length=200)
    department    = models.ForeignKey('departments.Department', on_delete=models.CASCADE)
    complaint     = models.OneToOneField('complaints.Complaint', null=True, blank=True, on_delete=models.SET_NULL)
    amount        = models.DecimalField(max_digits=14, decimal_places=2)
    fiscal_year   = models.CharField(max_length=9, default=get_fiscal_year)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)
    approved_by   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    rejection_reason = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} – ৳{self.amount} ({self.status})"
