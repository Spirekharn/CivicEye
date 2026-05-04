from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.complaint_list,    name='complaint_list'),
    path('create/',                 views.complaint_create,  name='complaint_create'),
    path('<int:pk>/',               views.complaint_detail,  name='complaint_detail'),
    path('admin/all/',              views.admin_complaints,  name='admin_complaints'),
    path('<int:pk>/assign/',        views.assign_complaint,  name='assign_complaint'),
    path('surveyor/queue/',         views.surveyor_queue,    name='surveyor_queue'),
    path('<int:pk>/survey/',        views.submit_survey,     name='submit_survey'),
    path('worker/tasks/',           views.worker_tasks,      name='worker_tasks'),
    path('<int:pk>/status/',        views.update_status,     name='update_status'),
    path('<int:pk>/assign-worker/', views.assign_worker,     name='assign_worker'),
]
