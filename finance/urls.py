from django.urls import path
from . import views
urlpatterns = [
    path('',                             views.finance_dashboard, name='finance_dashboard'),
    path('allocate/',                    views.allocate_budget,   name='allocate_budget'),
    path('expenses/',                    views.expense_list,      name='expense_list'),
    path('expense/<int:pk>/approve/',    views.approve_expense,   name='approve_expense'),
]
