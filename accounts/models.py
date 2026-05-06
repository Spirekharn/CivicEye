from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('citizen',    'Citizen'),
        ('worker',     'Field Worker'),
        ('technician', 'Technician'),
        ('surveyor',   'Surveyor'),
        ('admin',      'Department Admin'),
        ('super_admin','Super Admin'),
    ]
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark')]

    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone      = models.CharField(max_length=20, blank=True)
    address    = models.TextField(blank=True)
    theme      = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    department = models.ForeignKey(
        'departments.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='staff'
    )
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def is_field_staff(self):
        return self.role in ('worker', 'technician', 'surveyor')

    def is_management(self):
        return self.role in ('admin', 'super_admin')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
