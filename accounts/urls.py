from django.urls import path
from . import views

urlpatterns = [
    path('register/',  views.register_view,       name='register'),
    path('login/',     views.login_view,           name='login'),
    path('logout/',    views.logout_view,          name='logout'),
    path('profile/',   views.profile_view,         name='profile'),
    path('dashboard/', views.dashboard_view,       name='dashboard'),
    path('users/',     views.admin_users_view,     name='admin_users'),
    path('users/<int:user_id>/department/', views.update_user_department, name='update_user_department'),
    path('users/<int:user_id>/toggle/',     views.toggle_user_active,     name='toggle_user'),
    path('users/<int:user_id>/role/',       views.update_user_role,       name='update_user_role'),
    path('users/<int:user_id>/dept-head/',  views.toggle_dept_head,       name='toggle_dept_head'),
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('faq/',        views.faq_view,            name='faq'),
    path('contact/',    views.contact_view,        name='contact'),
    path('privacy/',    views.privacy_view,        name='privacy'),
    path('terms/',      views.terms_view,          name='terms'),
]
