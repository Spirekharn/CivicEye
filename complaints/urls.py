from django.urls import path
from .views import create_complaint

from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_complaint, name='create_complaint'),
    path('', views.complaint_list, name='complaint_list'),
    path('<int:id>/', views.complaint_detail, name='complaint_detail'),
    path('assign/<int:id>/', views.assign_complaint, name='assign_complaint'),
    path('status/<int:id>/<str:status>/', views.update_status, name='update_status'),
    path('assign/<int:id>/', views.assign_roles, name='assign_roles'),
    path('approve/<int:id>/', views.approve_budget, name='approve_budget'),
]