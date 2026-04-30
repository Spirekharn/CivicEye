from django.db import models

# Create your models here.
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # budget system
    total_budget = models.FloatField(default=0)
    remaining_budget = models.FloatField(default=0)
    def __str__(self):
        return self.name
class Expense(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    complaint_id = models.IntegerField(null=True, blank=True)

    amount = models.FloatField()
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.department.name} - {self.amount}"