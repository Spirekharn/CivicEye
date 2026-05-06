from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('citizen',    'Citizen'),
        ('worker',     'Field Worker'),
        ('technician', 'Technician'),
        ('surveyor',   'Surveyor'),
        ('admin',      'Department Admin'),
        ('finance',    'Finance Officer'),
        ('super_admin','Super Admin'),
    ]
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark')]

    role                = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone               = models.CharField(max_length=20, blank=True)
    address             = models.TextField(blank=True)
    theme               = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    department          = models.ForeignKey(
        'departments.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='staff'
    )
    profile_picture     = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_department_head  = models.BooleanField(default=False)

    def is_field_staff(self):
        return self.role in ('worker', 'technician', 'surveyor')

    def is_management(self):
        return self.role in ('admin', 'finance', 'super_admin')

    def is_finance(self):
        return self.role == 'finance'

    def is_dept_head(self):
        return self.role == 'admin' and self.is_department_head

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
