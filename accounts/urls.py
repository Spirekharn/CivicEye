from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    # register
    path('register/', views.register_view, name='register'),
    # login
    path('login/', views.login_view, name='login'),
    # logout
    path('logout/', views.logout_view, name='logout'),
    # dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # create superadmin
    path('create-superadmin/', views.create_superadmin, name='create_superadmin'),
    # about
    path('about/', views.about_view, name='about'),
    #worker dashborad
    path('worker/', views.worker_dashboard, name='worker_dashboard'),
]