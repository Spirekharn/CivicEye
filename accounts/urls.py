from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view,      name='register'),
    path('login/',    views.login_view,          name='login'),
    path('logout/',   views.logout_view,         name='logout'),
    path('profile/',  views.profile_view,        name='profile'),
    path('dashboard/',views.dashboard_view,      name='dashboard'),
    path('users/',    views.admin_users_view,     name='admin_users'),
    path('users/<int:user_id>/department/', views.update_user_department, name='update_user_department'),
    path('users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user'),
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
]
