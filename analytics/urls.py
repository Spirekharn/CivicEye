from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.analytics_dashboard,    name='analytics_dashboard'),
    path('api/by-category/',      views.api_by_category,        name='api_by_category'),
    path('api/by-status/',        views.api_by_status,          name='api_by_status'),
    path('api/resolution-trend/', views.api_resolution_trend,   name='api_resolution_trend'),
    path('api/dept-performance/', views.api_dept_performance,   name='api_dept_performance'),
    path('api/workload/',         views.api_workload,           name='api_workload'),
    path('api/budget-utilisation/', views.api_budget_utilisation, name='api_budget_utilisation'),
    path('api/monthly-volume/',   views.api_monthly_volume,     name='api_monthly_volume'),
]
