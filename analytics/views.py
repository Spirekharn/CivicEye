from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta


def _check_access(user):
    """Returns True if the user may view analytics."""
    return user.role in ('super_admin', 'finance', 'admin')


def _base_qs(user):
    """Scoped complaint queryset — admin sees only their department."""
    from complaints.models import Complaint
    if user.role == 'admin' and user.department:
        return Complaint.objects.filter(
            Q(department=user.department) | Q(department__isnull=True)
        )
    return Complaint.objects.all()


@login_required
def analytics_dashboard(request):
    if not _check_access(request.user):
        return redirect('dashboard')
    return render(request, 'analytics/dashboard.html')


@login_required
def api_by_category(request):
    if not _check_access(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    qs = _base_qs(request.user).values('category').annotate(count=Count('id')).order_by('-count')
    from complaints.models import CATEGORY_CHOICES
    label_map = dict(CATEGORY_CHOICES)
    data = [{'category': label_map.get(r['category'], r['category']), 'count': r['count']} for r in qs]
    return JsonResponse({'data': data})


@login_required
def api_by_status(request):
    if not _check_access(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    qs = _base_qs(request.user).values('status').annotate(count=Count('id')).order_by('-count')
    from complaints.models import STATUS_CHOICES
    label_map = dict(STATUS_CHOICES)
    data = [{'status': label_map.get(r['status'], r['status']), 'count': r['count']} for r in qs]
    return JsonResponse({'data': data})


@login_required
def api_resolution_trend(request):
    if not _check_access(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    cutoff = timezone.now() - timedelta(days=30)
    qs = (
        _base_qs(request.user)
        .filter(status__in=['resolved', 'closed'], updated_at__gte=cutoff)
        .annotate(day=TruncDate('updated_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    data = [{'date': str(r['day']), 'count': r['count']} for r in qs]
    return JsonResponse({'data': data})


@login_required
def api_dept_performance(request):
    if not _check_access(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    from complaints.models import Complaint, ComplaintFeedback
    from departments.models import Department
    depts = Department.objects.filter(is_active=True)
    result = []
    for dept in depts:
        total = Complaint.objects.filter(department=dept).count()
        resolved = Complaint.objects.filter(department=dept, status__in=['resolved', 'closed']).count()
        avg_rating = ComplaintFeedback.objects.filter(
            complaint__department=dept
        ).aggregate(avg=Avg('rating'))['avg']
        pct = round(resolved / total * 100) if total else 0
        result.append({
            'department': dept.name,
            'total': total,
            'resolved': resolved,
            'resolution_pct': pct,
            'avg_rating': round(avg_rating, 2) if avg_rating else None,
        })
    result.sort(key=lambda x: x['resolution_pct'], reverse=True)
    return JsonResponse({'data': result[:15]})  # top 15 departments


@login_required
def api_workload(request):
    if not _check_access(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    from complaints.models import Complaint
    surveyors = (
        Complaint.objects.filter(assigned_surveyor__isnull=False)
        .values('assigned_surveyor__username', 'assigned_surveyor__first_name', 'assigned_surveyor__last_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    workers = (
        Complaint.objects.filter(assigned_worker__isnull=False)
        .values('assigned_worker__username', 'assigned_worker__first_name', 'assigned_worker__last_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    def _name(row, prefix):
        fn = row.get(f'{prefix}__first_name') or ''
        ln = row.get(f'{prefix}__last_name') or ''
        full = (fn + ' ' + ln).strip()
        return full or row[f'{prefix}__username']

    surveyor_data = [{'name': _name(r, 'assigned_surveyor'), 'count': r['count']} for r in surveyors]
    worker_data   = [{'name': _name(r, 'assigned_worker'),   'count': r['count']} for r in workers]
    return JsonResponse({'surveyors': surveyor_data, 'workers': worker_data})


@login_required
def api_budget_utilisation(request):
    if request.user.role not in ('finance', 'super_admin'):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    from departments.models import Department
    from finance.models import DepartmentBudget, Expense, get_fiscal_year
    fy = get_fiscal_year()
    budgets = DepartmentBudget.objects.filter(fiscal_year=fy).select_related('department')
    spent_map = (
        Expense.objects.filter(fiscal_year=fy, status='approved')
        .values('department_id')
        .annotate(total=Sum('amount'))
    )
    spent_dict = {e['department_id']: float(e['total']) for e in spent_map}
    result = []
    for b in budgets:
        allocated = float(b.allocated_amount)
        spent = spent_dict.get(b.department_id, 0)
        result.append({
            'department': b.department.name,
            'allocated': allocated,
            'spent': spent,
            'remaining': allocated - spent,
        })
    result.sort(key=lambda x: x['allocated'], reverse=True)
    return JsonResponse({'data': result, 'fiscal_year': fy})


@login_required
def api_monthly_volume(request):
    if not _check_access(request.user):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if request.user.role not in ('finance', 'super_admin'):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    from complaints.models import Complaint
    cutoff = timezone.now() - timedelta(days=180)
    qs = (
        _base_qs(request.user)
        .filter(created_at__gte=cutoff)
        .annotate(month=TruncMonth('created_at'))
        .values('month', 'city_corp')
        .annotate(count=Count('id'))
        .order_by('month', 'city_corp')
    )
    # Pivot into {city_corp: [{month, count}]} structure for Chart.js
    from collections import defaultdict
    pivot = defaultdict(list)
    months_set = set()
    for r in qs:
        month_str = r['month'].strftime('%b %Y')
        pivot[r['city_corp']].append({'month': month_str, 'count': r['count']})
        months_set.add(month_str)
    months = sorted(months_set)
    # Build datasets
    datasets = []
    for corp, entries in sorted(pivot.items()):
        month_map = {e['month']: e['count'] for e in entries}
        datasets.append({
            'label': corp,
            'data': [month_map.get(m, 0) for m in months],
        })
    return JsonResponse({'months': months, 'datasets': datasets})
