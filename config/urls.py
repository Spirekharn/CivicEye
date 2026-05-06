from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as av

admin.site.site_header  = "CivicEye Super Admin"
admin.site.site_title   = "CivicEye"
admin.site.index_title  = "System Control Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',        av.home_view,     name='home'),
    path('about/',  av.about_view,    name='about'),
    path('accounts/', include('accounts.urls')),
    path('complaints/', include('complaints.urls')),
    path('departments/', include('departments.urls')),
    path('finance/', include('finance.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
