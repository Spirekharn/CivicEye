from django.contrib import admin
from .models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name','slug','city_corp','is_active')
    list_filter  = ('city_corp','is_active')
    search_fields = ('name', 'slug', 'city_corp')
    list_editable = ('is_active',)
