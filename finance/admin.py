from django.contrib import admin
from .models import DepartmentBudget, Expense

@admin.register(DepartmentBudget)
class DepartmentBudgetAdmin(admin.ModelAdmin):
    list_display = ('department', 'fiscal_year', 'allocated_amount', 'allocated_by', 'created_at')
    list_filter = ('fiscal_year', 'department__city_corp')
    search_fields = ('department__name', 'department__city_corp')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'amount', 'fiscal_year', 'status', 'approved_by', 'created_at')
    list_filter = ('status', 'fiscal_year', 'department__city_corp')
    search_fields = ('title', 'department__name', 'complaint__title')
