from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request):
    from django.core.paginator import Paginator
    filt = request.GET.get('filter', 'all')
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    if filt == 'unread':
        notifs = notifs.filter(is_read=False)
    elif filt == 'read':
        notifs = notifs.filter(is_read=True)
    page_params = request.GET.copy()
    page_params.pop('page', None)
    paginator = Paginator(notifs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'notifications/list.html', {
        'notifications': page_obj,
        'page_obj': page_obj,
        'page_params': page_params,
        'active_filter': filt,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    })


@login_required
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    return redirect('notification_list')


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notification_list')
