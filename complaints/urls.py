from django.urls import path
from .views import create_complaint

urlpatterns = [
    path('create/', create_complaint, name='create_complaint'),
]