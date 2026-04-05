from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('citizen-dashboard/', citizen_dashboard, name='citizen_dashboard'),
    path('worker-dashboard/', worker_dashboard, name='worker_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]