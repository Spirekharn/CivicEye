from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username','email','role','department','is_active','date_joined')
    list_filter   = ('role','is_active','department')
    search_fields = ('username','email','first_name','last_name')
    list_editable = ('role', 'department', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('CivicEye Profile', {'fields': ('role','phone','address','department','theme','profile_picture')}),
    )
