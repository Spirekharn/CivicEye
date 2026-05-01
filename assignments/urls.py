from django.urls import path
from . import views

urlpatterns = [
    path('report/<int:id>/', views.create_report, name='create_report'),
]