from django.urls import path
from django.contrib.auth import views as auth_views
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
    # Password reset (Django built-in)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/email/password_reset_email.txt',
             subject_template_name='accounts/email/password_reset_subject.txt',
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]
