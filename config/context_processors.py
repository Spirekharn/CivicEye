from django.conf import settings
from notifications.models import Notification

def global_context(request):
    count = 0
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    hotlines = getattr(settings, 'CITY_CORP_HOTLINES', {})
    return {
        'unread_notif_count': count,
        'HOTLINES': hotlines,
        'DEFAULT_HOTLINE': hotlines.get('default', {'shortcode': '333', 'emergency': '999'}),
    }
