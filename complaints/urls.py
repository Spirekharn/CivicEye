from django.urls import path
from .views import create_complaint

from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_complaint, name='create_complaint'),
    path('', views.complaint_list, name='complaint_list'),  # 👈 IMPORTANT
]