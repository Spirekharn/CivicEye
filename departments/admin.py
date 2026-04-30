from django.contrib import admin

# Register your models here.
from .models import Department, Expense

admin.site.register(Department)
admin.site.register(Expense)