from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from django.core.paginator import Paginator, InvalidPage
from decimal import Decimal, InvalidOperation
import math
from .models import (Complaint, ComplaintStatusHistory, SurveyReport,
                     ComplaintFeedback, ComplaintTransferRequest)
from .models import PRIORITY_CHOICES
from .location_router import detect_city_corp, get_department_for_complaint
from accounts.models import User
from departments.models import Department, CITY_CORP_CHOICES
from notifications.models import Notification
from finance.models import Expense, DepartmentBudget, get_fiscal_year


def _notify(user, title, msg, ntype, complaint=None):
    Notification.objects.create(user=user, title=title, message=msg,
                                 notification_type=ntype, complaint=complaint)


def _log_event(complaint, status, user, notes='', event_type='status_change'):
    ComplaintStatusHistory.objects.create(
        complaint=complaint, status=status, changed_by=user,
        notes=notes, event_type=event_type)


def _log(complaint, status, user, notes=''):
    _log_event(complaint, status, user, notes, 'status_change')


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _can_view_complaint(user, complaint):
    if user.role in ('super_admin', 'finance'):
        return True
    if user.role == 'citizen':
        return (complaint.citizen_id == user.id or
                complaint.co_reporters.filter(id=user.id).exists())
    if user.role == 'admin':
        return user.department_id and (
            complaint.department_id == user.department_id or complaint.department_id is None
        )
    if user.role == 'surveyor':
        return complaint.assigned_surveyor_id == user.id
    if user.role in ('worker', 'technician'):
        return complaint.assigned_worker_id == user.id
    return False


def _parse_money(value):
    try:
        amount = Decimal(value or '0')
    except (InvalidOperation, TypeError):
        raise ValueError('Cost estimates must be valid numbers.')
    if amount < 0:
        raise ValueError('Cost estimates cannot be negative.')
    return amount


def _parse_days(value):
    try:
        days = int(value or 1)
    except (TypeError, ValueError):
        raise ValueError('Estimated days must be a whole number.')
    if days < 1 or days > 365:
        raise ValueError('Estimated days must be between 1 and 365.')
    return days


_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
_ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


def _validate_image(uploaded_file):
    """Raise ValueError if the uploaded file exceeds size or type limits."""
    if uploaded_file.size > _MAX_UPLOAD_BYTES:
        raise ValueError('Image must be no larger than 10 MB.')
    if uploaded_file.content_type not in _ALLOWED_IMAGE_TYPES:
        raise ValueError('Only JPG, PNG, WebP, or GIF images are accepted.')


STATUS_CHOICES = [
    ('submitted', 'Submitted'), ('under_review', 'Under Review'), ('assigned', 'Assigned'),
    ('surveying', 'Surveying'), ('survey_done', 'Survey Done'), ('budget_pending', 'Budget Pending'),
    ('budget_approved', 'Budget Approved'), ('worker_assigned', 'Worker Assigned'),
    ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed'), ('rejected', 'Rejected'),
]
CATEGORY_CHOICES = [
    ('roads', 'Roads & Infrastructure'), ('water', 'Water & Sewerage'),
    ('electricity', 'Electricity & Lights'), ('sanitation', 'Sanitation & Waste'),
    ('parks', 'Parks & Recreation'), ('health', 'Public Health'),
    ('building', 'Building & Construction'), ('transport', 'Transport & Traffic'),
    ('environment', 'Environment & Drainage'), ('fire', 'Fire & Emergency'),
    ('it', 'IT & Technology'), ('admin_dept', 'General Administration'),
    ('other', 'Other'),
]


@login_required
def complaint_list(request):
    u = request.user
    if u.role == 'citizen':
        qs = Complaint.objects.filter(
            Q(citizen=u) | Q(co_reporters=u)
        ).distinct()
    elif u.role == 'surveyor':
        qs = Complaint.objects.filter(assigned_surveyor=u)
    elif u.role in ('worker', 'technician'):
        qs = Complaint.objects.filter(assigned_worker=u)
    elif u.role == 'admin':
        qs = Complaint.objects.filter(department=u.department)
    else:
        qs = Complaint.objects.all()

    q = request.GET.get('q', '')
    status_f = request.GET.get('status', '')
    cat_f = request.GET.get('category', '')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(location_text__icontains=q) | Q(description__icontains=q))
    if status_f:
        qs = qs.filter(status=status_f)
    if cat_f:
        qs = qs.filter(category=cat_f)

    page_params = request.GET.copy()
    page_params.pop('page', None)
    qs = qs.select_related('department', 'citizen').order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'complaints/list.html', {
        'complaints': page_obj,
        'page_obj': page_obj,
        'page_params': page_params,
        'status_choices': STATUS_CHOICES,
        'category_choices': CATEGORY_CHOICES,
    })


@login_required
def complaint_create(request):
    if request.user.role not in ('citizen', 'super_admin'):
        messages.error(request, 'Only citizens can submit complaints.')
        return redirect('dashboard')
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        desc     = request.POST.get('description', '').strip()
        cat      = request.POST.get('category', '')
        priority = request.POST.get('priority', 'medium')
        dept_id  = request.POST.get('department', '')
        loc      = request.POST.get('location_text', '').strip()
        lat      = request.POST.get('latitude') or None
        lng      = request.POST.get('longitude') or None
        anon     = bool(request.POST.get('is_anonymous'))

        if not all([title, desc, cat, loc]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'complaints/create.html', _complaint_form_context(request.POST))
        if cat not in dict(CATEGORY_CHOICES):
            messages.error(request, 'Please choose a valid complaint category.')
            return render(request, 'complaints/create.html', _complaint_form_context(request.POST))
        if priority not in dict(PRIORITY_CHOICES):
            messages.error(request, 'Please choose a valid priority.')
            return render(request, 'complaints/create.html', _complaint_form_context(request.POST))

        city_corp = detect_city_corp(loc)
        if dept_id:
            dept = get_object_or_404(Department, id=dept_id, is_active=True)
            city_corp = dept.city_corp
        else:
            dept = get_department_for_complaint(cat, city_corp)

        c = Complaint(
            citizen=request.user, title=title, description=desc,
            category=cat, location_text=loc, city_corp=city_corp,
            department=dept, status='submitted', priority=priority,
            is_anonymous=anon,
        )
        if lat:
            try:
                c.latitude = float(lat)
            except (TypeError, ValueError):
                messages.error(request, 'Latitude must be a valid number.')
                return render(request, 'complaints/create.html', _complaint_form_context(request.POST))
        if lng:
            try:
                c.longitude = float(lng)
            except (TypeError, ValueError):
                messages.error(request, 'Longitude must be a valid number.')
                return render(request, 'complaints/create.html', _complaint_form_context(request.POST))
        if request.FILES.get('image'):
            try:
                _validate_image(request.FILES['image'])
                c.image = request.FILES['image']
            except ValueError as exc:
                messages.error(request, str(exc))
                return render(request, 'complaints/create.html', _complaint_form_context(request.POST))
        c.save()
        _log(c, 'submitted', request.user, 'Complaint submitted.')

        if dept:
            for admin in User.objects.filter(role='admin', department=dept, is_active=True):
                _notify(admin, 'New Complaint', f'New complaint: {c.title}', 'complaint_submitted', c)
        else:
            for sa in User.objects.filter(role='super_admin', is_active=True):
                _notify(sa, 'Unrouted Complaint', f'Could not route complaint in {city_corp}: {c.title}', 'complaint_submitted', c)

        _run_duplicate_check(c, request.user)

        # send a quick acknowledgment to the citizen if they have an email on file
        if not c.is_anonymous and c.citizen.email:
            try:
                from django.core.mail import send_mail
                send_mail(
                    subject=f'[CivicEye] Complaint received — {c.title}',
                    message=(
                        f'Hi {c.citizen.first_name or c.citizen.username},\n\n'
                        f'Your complaint "{c.title}" has been received.\n'
                        f'Reference ID: #{c.pk}\n\n'
                        f'You can track progress at: /complaints/{c.pk}/\n\n'
                        f'— CivicEye Team'
                    ),
                    from_email=None,
                    recipient_list=[c.citizen.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # never crash the complaint submission because of email

        messages.success(request, f'Complaint submitted! Routed to {city_corp} — {dept.name if dept else "system"}.')
        return redirect('complaint_detail', pk=c.pk)

    return render(request, 'complaints/create.html', _complaint_form_context())


def _run_duplicate_check(new_complaint, submitter):
    from datetime import timedelta
    from django.utils import timezone

    window = timezone.now() - timedelta(hours=6)
    candidates = Complaint.objects.filter(
        category=new_complaint.category,
        created_at__gte=window,
        is_duplicate=False,
    ).exclude(pk=new_complaint.pk)

    if new_complaint.latitude and new_complaint.longitude:
        for candidate in candidates:
            if candidate.latitude and candidate.longitude:
                dist = _haversine(
                    new_complaint.latitude, new_complaint.longitude,
                    candidate.latitude, candidate.longitude,
                )
                if dist <= 500:
                    new_complaint.is_duplicate = True
                    new_complaint.duplicate_of = candidate
                    new_complaint.save(update_fields=['is_duplicate', 'duplicate_of'])
                    candidate.co_reporters.add(submitter)
                    _log_event(new_complaint, new_complaint.status, submitter,
                               f'Marked as duplicate of #{candidate.pk}.', 'merged_as_duplicate')
                    _log_event(candidate, candidate.status, submitter,
                               f'Complaint #{new_complaint.pk} merged as duplicate.', 'merged_as_primary')
                    _notify(submitter, 'Similar Report Found',
                            f'Your complaint is similar to an existing report: "{candidate.title}". You have been added as a co-reporter.',
                            'complaint_merged', candidate)
                    _notify(candidate.citizen, 'Duplicate Report Filed',
                            f'Another citizen filed a similar complaint to yours: "{candidate.title}".',
                            'complaint_merged', candidate)
                    return


def _complaint_form_context(post=None):
    return {
        'departments': Department.objects.filter(is_active=True).order_by('city_corp', 'name'),
        'priority_choices': PRIORITY_CHOICES,
        'post': post,
    }


@login_required
def complaint_detail(request, pk):
    c = get_object_or_404(Complaint, pk=pk)
    u = request.user

    if not _can_view_complaint(u, c):
        messages.error(request, 'Access denied.')
        return redirect('complaint_list')

    history = c.history.order_by('created_at')
    try:
        survey = c.survey_report
    except SurveyReport.DoesNotExist:
        survey = None
    try:
        feedback = c.feedback
    except ComplaintFeedback.DoesNotExist:
        feedback = None

    if request.method == 'POST' and request.POST.get('action') == 'feedback':
        if u.role == 'citizen' and c.citizen == u and c.status in ('resolved', 'closed') and not feedback:
            try:
                rating = int(request.POST.get('rating', 3))
            except (TypeError, ValueError):
                rating = 3
            rating = max(1, min(5, rating))
            comment = request.POST.get('comment', '').strip()
            ComplaintFeedback.objects.create(complaint=c, citizen=u, rating=rating, comment=comment)
            messages.success(request, 'Thank you for your feedback!')
            return redirect('complaint_detail', pk=pk)

    if request.method == 'POST' and request.POST.get('action') == 'override':
        if u.role in ('admin', 'super_admin'):
            new_status = request.POST.get('new_status')
            notes = request.POST.get('notes', '')
            if new_status:
                c.status = new_status
                if new_status == 'resolved':
                    c.resolution_notes = notes
                c.save()
                _log(c, new_status, u, notes or f'Status overridden to {new_status} by {u.username}.')
                messages.success(request, f'Status updated to {new_status}.')
                return redirect('complaint_detail', pk=pk)

    if request.method == 'POST' and request.POST.get('action') == 'department':
        if u.role in ('admin', 'super_admin'):
            dept_id = request.POST.get('department')
            if u.role == 'admin' and u.department_id:
                dept = u.department
            else:
                dept = get_object_or_404(Department, id=dept_id, is_active=True)
            c.department = dept
            c.city_corp = dept.city_corp
            if c.status == 'submitted':
                c.status = 'under_review'
            c.save(update_fields=['department', 'city_corp', 'status', 'updated_at'])
            _log(c, c.status, u, f'Department assigned to {dept.name}.')
            messages.success(request, f'Department set to {dept.name}.')
            return redirect('complaint_detail', pk=pk)

    if request.method == 'POST' and request.POST.get('action') == 'request_transfer':
        if u.role == 'admin' and c.department == u.department:
            to_dept_id = request.POST.get('to_department')
            reason = request.POST.get('transfer_reason', '').strip()
            if to_dept_id and reason:
                to_dept = get_object_or_404(Department, id=to_dept_id, is_active=True)
                if not c.transfer_requests.filter(status='pending').exists():
                    tr = ComplaintTransferRequest.objects.create(
                        complaint=c,
                        from_department=c.department,
                        to_department=to_dept,
                        reason=reason,
                        requested_by=u,
                    )
                    _log_event(c, c.status, u,
                               f'Transfer requested to {to_dept.name}. Reason: {reason}',
                               'transfer_requested')
                    for sa in User.objects.filter(role='super_admin', is_active=True):
                        _notify(sa, 'Transfer Request',
                                f'Dept "{c.department.name}" requests transfer of complaint "{c.title}" to "{to_dept.name}".',
                                'transfer_requested', c)
                    for head in User.objects.filter(role='admin', department=to_dept,
                                                    is_active=True, is_department_head=True):
                        _notify(head, 'Incoming Transfer Request',
                                f'Complaint "{c.title}" may be transferred to your department.',
                                'transfer_requested', c)
                    messages.success(request, 'Transfer request submitted.')
                else:
                    messages.warning(request, 'A transfer request is already pending for this complaint.')
            else:
                messages.error(request, 'Please select a destination department and provide a reason.')
            return redirect('complaint_detail', pk=pk)

    if request.method == 'POST' and request.POST.get('action') == 'manual_merge':
        if u.role in ('admin', 'super_admin'):
            try:
                secondary_id = int(request.POST.get('secondary_id', 0))
            except (TypeError, ValueError):
                secondary_id = 0
            if secondary_id and secondary_id != c.pk:
                try:
                    secondary = Complaint.objects.get(pk=secondary_id)
                    secondary.is_duplicate = True
                    secondary.duplicate_of = c
                    secondary.save(update_fields=['is_duplicate', 'duplicate_of'])
                    c.co_reporters.add(secondary.citizen)
                    _log_event(c, c.status, u, f'Complaint #{secondary.pk} manually merged as duplicate.', 'merged_as_primary')
                    _log_event(secondary, secondary.status, u, f'Manually merged as duplicate of #{c.pk}.', 'merged_as_duplicate')
                    _notify(secondary.citizen, 'Complaint Merged',
                            f'Your complaint "{secondary.title}" has been merged with "{c.title}". You have been added as a co-reporter.',
                            'complaint_merged', c)
                    _notify(c.citizen, 'Complaint Merged',
                            f'Complaint #{secondary.pk} has been merged into your complaint "{c.title}".',
                            'complaint_merged', c)
                    messages.success(request, f'Complaint #{secondary_id} merged as duplicate.')
                except Complaint.DoesNotExist:
                    messages.error(request, f'Complaint #{secondary_id} not found.')
            else:
                messages.error(request, 'Invalid complaint ID for merge.')
            return redirect('complaint_detail', pk=pk)

    if request.method == 'POST' and request.POST.get('action') == 'surveyor_reject':
        if u.role == 'surveyor' and c.assigned_surveyor == u and c.status in ('assigned', 'surveying'):
            reason = request.POST.get('reject_reason', '').strip()
            if not reason:
                messages.error(request, 'Please provide a reason for rejection.')
            else:
                c.status = 'rejected'
                c.save(update_fields=['status', 'updated_at'])
                _log(c, 'rejected', u, f'Surveyor marked complaint as invalid. Reason: {reason}')
                _notify(c.citizen, 'Complaint Rejected',
                        f'Your complaint "{c.title}" could not be verified on-site. Reason: {reason}',
                        'general', c)
                if c.department:
                    for admin in User.objects.filter(role='admin', department=c.department, is_active=True):
                        _notify(admin, 'Complaint Rejected by Surveyor',
                                f'Surveyor marked "{c.title}" as invalid. Reason: {reason}',
                                'general', c)
                messages.success(request, 'Complaint marked as invalid.')
            return redirect('complaint_detail', pk=pk)

    if request.method == 'POST' and request.POST.get('action') == 'request_resurvey':
        if u.role in ('worker', 'technician') and c.assigned_worker == u and c.status in ('worker_assigned', 'in_progress'):
            reason = request.POST.get('resurvey_reason', '').strip()
            if not reason:
                messages.error(request, 'Please describe why a resurvey is needed.')
            else:
                c.status = 'under_review'
                c.assigned_worker = None
                c.assigned_surveyor = None
                c.save(update_fields=['status', 'assigned_worker', 'assigned_surveyor', 'updated_at'])
                _log(c, 'under_review', u, f'Worker requested resurvey. Reason: {reason}')
                if c.department:
                    for admin in User.objects.filter(role='admin', department=c.department, is_active=True):
                        _notify(admin, 'Resurvey Requested',
                                f'Worker flagged "{c.title}" as needing resurvey. Reason: {reason}',
                                'general', c)
                messages.success(request, 'Resurvey request submitted. Admin has been notified.')
            return redirect('complaint_detail', pk=pk)

    dept_surveyors = []
    dept_workers = []
    if u.role in ('admin', 'super_admin') and c.department:
        dept_surveyors = User.objects.filter(role='surveyor', department=c.department, is_active=True)
        needed = c.required_worker_type()
        dept_workers = User.objects.filter(role=needed, department=c.department, is_active=True)

    expense = None
    try:
        expense = c.expense
    except Expense.DoesNotExist:
        expense = None

    pending_transfer = c.transfer_requests.filter(status='pending').first()
    co_reporters = c.co_reporters.all()
    transfer_requests = c.transfer_requests.select_related(
        'from_department', 'to_department', 'requested_by', 'reviewed_by'
    ).order_by('-created_at')

    from django.conf import settings
    hotline = settings.CITY_CORP_HOTLINES.get(c.city_corp, settings.CITY_CORP_HOTLINES['default'])

    show_actual_budget = u.role in ('admin', 'finance', 'super_admin')
    survey_cost_range = None
    if survey and not show_actual_budget:
        cost = float(survey.estimated_cost)
        low  = round(cost * 0.70 / 1000) * 1000
        high = round(cost * 1.30 / 1000) * 1000
        survey_cost_range = (low, high)

    return render(request, 'complaints/detail.html', {
        'c': c, 'history': history, 'survey': survey,
        'feedback': feedback, 'expense': expense,
        'dept_surveyors': dept_surveyors,
        'dept_workers': dept_workers,
        'status_choices': STATUS_CHOICES,
        'departments': Department.objects.filter(is_active=True).order_by('city_corp', 'name'),
        'progress': c.get_status_progress(),
        'co_reporters': co_reporters,
        'pending_transfer': pending_transfer,
        'transfer_requests': transfer_requests,
        'hotline': hotline,
        'show_actual_budget': show_actual_budget,
        'survey_cost_range': survey_cost_range,
    })


@login_required
def admin_complaints(request):
    if request.user.role not in ('admin', 'finance', 'super_admin'):
        return redirect('dashboard')
    u = request.user
    if u.role == 'admin':
        qs = Complaint.objects.filter(Q(department=u.department) | Q(department__isnull=True))
    else:
        qs = Complaint.objects.all()

    q        = request.GET.get('q', '')
    status_f = request.GET.get('status', '')
    cat_f    = request.GET.get('category', '')
    prio_f   = request.GET.get('priority', '')
    corp_f   = request.GET.get('corp', '')

    if q:        qs = qs.filter(Q(title__icontains=q) | Q(location_text__icontains=q) | Q(citizen__username__icontains=q))  # noqa: E501
    if status_f: qs = qs.filter(status=status_f)
    if cat_f:    qs = qs.filter(category=cat_f)
    if prio_f:   qs = qs.filter(priority=prio_f)
    if corp_f:   qs = qs.filter(city_corp=corp_f)

    page_params = request.GET.copy()
    page_params.pop('page', None)

    # stats based on the full dept-scoped queryset, not the current search filters
    base_qs = (
        Complaint.objects.filter(Q(department=u.department) | Q(department__isnull=True))
        if u.role == 'admin' else Complaint.objects.all()
    )

    qs = qs.select_related('department', 'citizen').order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'complaints/admin_list.html', {
        'complaints': page_obj,
        'page_obj': page_obj,
        'page_params': page_params,
        'status_choices': STATUS_CHOICES,
        'category_choices': CATEGORY_CHOICES,
        'corps': Complaint.objects.exclude(city_corp='').values_list('city_corp', flat=True).distinct(),
        'total': base_qs.count(),
        'pending': base_qs.filter(status__in=['submitted', 'under_review']).count(),
        'in_progress': base_qs.filter(status='in_progress').count(),
        'resolved': base_qs.filter(status__in=['resolved', 'closed']).count(),
    })


@login_required
def assign_complaint(request, pk):
    if request.user.role not in ('admin', 'super_admin'):
        return redirect('dashboard')
    c = get_object_or_404(Complaint, pk=pk)
    u = request.user
    if u.role == 'admin' and c.department and c.department != u.department:
        messages.error(request, 'Access denied.')
        return redirect('admin_complaints')

    dept = c.department
    departments = Department.objects.filter(is_active=True).order_by('city_corp', 'name')
    if u.role == 'admin' and u.department_id:
        departments = departments.filter(id=u.department_id)
    surveyors = User.objects.filter(role='surveyor', department=dept, is_active=True) if dept else []

    if request.method == 'POST':
        dept_id = request.POST.get('department', '')
        sid     = request.POST.get('surveyor')
        prio    = request.POST.get('priority', c.priority)
        notes   = request.POST.get('notes', '')
        if prio not in dict(PRIORITY_CHOICES):
            messages.error(request, 'Please choose a valid priority.')
            return redirect('assign_complaint', pk=pk)
        if dept_id:
            if u.role == 'admin' and u.department_id:
                dept = u.department
            else:
                dept = get_object_or_404(Department, id=dept_id, is_active=True)
            c.department = dept
            c.city_corp = dept.city_corp
            c.priority = prio
            if c.status == 'submitted':
                c.status = 'under_review'
            c.save(update_fields=['department', 'city_corp', 'priority', 'status', 'updated_at'])
            _log(c, c.status, u, f'Department set to {dept.name}.')
            surveyors = User.objects.filter(role='surveyor', department=dept, is_active=True)
        if sid:
            sv = get_object_or_404(User, id=sid, role='surveyor', department=dept, is_active=True)
            c.assigned_surveyor = sv
            c.priority = prio
            c.status = 'assigned'
            c.save()
            _log(c, 'assigned', u, notes or f'Assigned to surveyor {sv.get_full_name()}.')
            _notify(sv, 'Survey Request', f'You have been assigned to survey: {c.title}', 'survey_request', c)
            _notify(c.citizen, 'Complaint Assigned', f'Your complaint "{c.title}" has been assigned for inspection.', 'complaint_assigned', c)
            messages.success(request, f'Assigned to {sv.get_full_name()}.')
            return redirect('complaint_detail', pk=pk)
        if dept_id:
            messages.success(request, f'Department updated to {dept.name}. Select a surveyor when one is available.')
            return redirect('assign_complaint', pk=pk)

    return render(request, 'complaints/assign.html', {
        'c': c,
        'surveyors': surveyors,
        'departments': departments,
        'priority_choices': PRIORITY_CHOICES,
    })


@login_required
def assign_worker(request, pk):
    if request.user.role not in ('admin', 'super_admin'):
        return redirect('dashboard')
    c = get_object_or_404(Complaint, pk=pk)
    u = request.user
    if u.role == 'admin' and c.department and c.department != u.department:
        messages.error(request, 'Access denied.')
        return redirect('admin_complaints')
    needed = c.required_worker_type()
    workers = User.objects.filter(role=needed, department=c.department, is_active=True) if c.department else []

    if request.method == 'POST':
        wid   = request.POST.get('worker')
        notes = request.POST.get('notes', '')
        if wid:
            # Enforce: worker assignment requires budget_approved status
            if c.status != 'budget_approved':
                messages.error(request, 'Worker can only be assigned after budget has been approved.')
                return redirect('complaint_detail', pk=pk)
            w = get_object_or_404(User, id=wid, role=needed, department=c.department, is_active=True)
            c.assigned_worker = w
            c.status = 'worker_assigned'
            c.save()
            _log(c, 'worker_assigned', u, notes or f'Assigned to {w.get_full_name()}.')
            _notify(w, 'Task Assigned', f'You have been assigned a task: {c.title}', 'worker_assigned', c)
            _notify(c.citizen, 'Worker Assigned', f'A {needed} has been assigned to fix your issue: {c.title}', 'worker_assigned', c)
            messages.success(request, f'Assigned to {w.get_full_name()}.')
            return redirect('complaint_detail', pk=pk)

    return render(request, 'complaints/assign_worker.html', {
        'c': c, 'workers': workers, 'needed': needed})


@login_required
def surveyor_queue(request):
    if request.user.role != 'surveyor':
        return redirect('dashboard')
    qs = Complaint.objects.filter(assigned_surveyor=request.user).order_by('-created_at')
    return render(request, 'complaints/surveyor_queue.html', {'complaints': qs})


@login_required
def submit_survey(request, pk):
    if request.user.role != 'surveyor':
        return redirect('dashboard')
    c = get_object_or_404(Complaint, pk=pk, assigned_surveyor=request.user)

    # Enforce: survey can only be submitted when complaint is in assigned or surveying state
    if c.status not in ('assigned', 'surveying'):
        messages.error(request, 'Survey can only be submitted for complaints in assigned or surveying status.')
        return redirect('complaint_detail', pk=pk)

    if request.method == 'POST':
        findings  = request.POST.get('findings', '').strip()
        materials = request.POST.get('materials_needed', '').strip()
        try:
            labour = _parse_money(request.POST.get('labor_estimate', 0))
            equip  = _parse_money(request.POST.get('equipment_estimate', 0))
            misc   = _parse_money(request.POST.get('misc_estimate', 0))
            days   = _parse_days(request.POST.get('estimated_days', 1))
        except ValueError as exc:
            messages.error(request, str(exc))
            return render(request, 'complaints/survey_form.html', {'c': c})
        prio_rec = request.POST.get('priority_recommendation', c.priority)

        if not findings:
            messages.error(request, 'Findings are required.')
            return render(request, 'complaints/survey_form.html', {'c': c})

        total = labour + equip + misc

        # validate survey image before entering the atomic block
        survey_img = request.FILES.get('survey_image')
        if survey_img:
            try:
                _validate_image(survey_img)
            except ValueError as exc:
                messages.error(request, str(exc))
                return render(request, 'complaints/survey_form.html', {'c': c})

        with transaction.atomic():
            sr, _ = SurveyReport.objects.update_or_create(
                complaint=c,
                defaults={
                    'surveyor': request.user,
                    'findings': findings,
                    'materials_needed': materials,
                    'labor_estimate': labour,
                    'equipment_estimate': equip,
                    'misc_estimate': misc,
                    'estimated_cost': total,
                    'priority_recommendation': prio_rec,
                    'estimated_days': days,
                }
            )
            if survey_img:
                sr.survey_image = survey_img
                sr.save()

            c.status = 'survey_done'
            c.priority = prio_rec
            c.save()
            _log(c, 'survey_done', request.user, f'Survey completed. Estimated cost: BDT {total:,.0f}.')

            if c.department:
                fiscal = get_fiscal_year()
                if not Expense.objects.filter(complaint=c).exists():
                    Expense.objects.create(
                        title=f'Survey estimate: {c.title[:80]}',
                        department=c.department, complaint=c,
                        amount=total, fiscal_year=fiscal, status='pending',
                    )
                    c.status = 'budget_pending'
                    c.save()
                    _log(c, 'budget_pending', request.user, 'Expense created, awaiting budget approval.')

        # notifications go outside the atomic block
        if c.department:
            for admin in User.objects.filter(role='admin', department=c.department, is_active=True):
                _notify(admin, 'Survey Completed',
                        f'Survey done for: {c.title}. Estimated cost: BDT {total:,.0f}. Awaiting budget approval.',
                        'survey_done', c)
            for fin in User.objects.filter(role='finance', is_active=True):
                _notify(fin, 'Expense Pending Approval',
                        f'New expense of BDT {total:,.0f} submitted for "{c.title}" — awaiting your approval.',
                        'survey_done', c)
        _notify(c.citizen, 'Survey Done',
                f'Your complaint "{c.title}" has been surveyed. Estimated resolution cost: BDT {total:,.0f}.',
                'survey_done', c)

        messages.success(request, f'Survey submitted. Total estimate: BDT {total:,.0f}.')
        return redirect('complaint_detail', pk=pk)

    return render(request, 'complaints/survey_form.html', {'c': c})


@login_required
def worker_tasks(request):
    if request.user.role not in ('worker', 'technician'):
        return redirect('dashboard')
    qs = Complaint.objects.filter(assigned_worker=request.user).order_by('-updated_at')
    return render(request, 'complaints/worker_tasks.html', {'complaints': qs})


@login_required
def update_status(request, pk):
    c = get_object_or_404(Complaint, pk=pk)
    u = request.user
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes      = request.POST.get('notes', '').strip()

        if u.role in ('worker', 'technician') and c.assigned_worker != u:
            messages.error(request, 'Access denied.')
            return redirect('worker_tasks')
        if u.role == 'surveyor' and c.assigned_surveyor != u:
            messages.error(request, 'Access denied.')
            return redirect('surveyor_queue')

        valid = {
            'worker':      ['in_progress', 'resolved'],
            'technician':  ['in_progress', 'resolved'],
            'surveyor':    ['surveying'],
            'admin':       ['under_review', 'assigned', 'worker_assigned', 'resolved', 'closed', 'rejected'],
            'finance':     [],
            'super_admin': list(dict(STATUS_CHOICES).keys()),
        }
        allowed = valid.get(u.role, [])
        if new_status not in allowed:
            messages.error(request, 'Invalid status transition.')
            return redirect('complaint_detail', pk=pk)

        # Workers/technicians must go through in_progress before resolving
        if u.role in ('worker', 'technician'):
            if new_status == 'in_progress' and c.status != 'worker_assigned':
                messages.error(request, 'Cannot move to in progress from the current status.')
                return redirect('complaint_detail', pk=pk)
            if new_status == 'resolved' and c.status != 'in_progress':
                messages.error(request, 'Please mark the task as In Progress first before resolving.')
                return redirect('complaint_detail', pk=pk)

        c.status = new_status
        if new_status == 'resolved' and notes:
            c.resolution_notes = notes
        if new_status == 'resolved' and request.FILES.get('completion_image'):
            try:
                _validate_image(request.FILES['completion_image'])
                c.completion_image = request.FILES['completion_image']
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect('complaint_detail', pk=pk)
        c.save()
        _log(c, new_status, u, notes or f'Status changed to {new_status} by {u.get_full_name()}.')

        if new_status == 'resolved':
            _notify(c.citizen, 'Issue Resolved',
                    f'Your complaint "{c.title}" has been resolved. Please rate the resolution.',
                    'complaint_resolved', c)
        elif new_status == 'rejected':
            _notify(c.citizen, 'Complaint Rejected',
                    f'Your complaint "{c.title}" has been rejected. Reason: {notes}',
                    'general', c)

        messages.success(request, f'Status updated to {new_status}.')
    return redirect('complaint_detail', pk=pk)


@login_required
def public_dashboard(request):
    if request.user.role != 'citizen':
        return redirect('dashboard')

    total = Complaint.objects.count()
    resolved = Complaint.objects.filter(status__in=['resolved', 'closed']).count()
    success_rate = round((resolved / total * 100) if total else 0)
    open_count = Complaint.objects.filter(
        status__in=['submitted', 'under_review', 'assigned', 'surveying',
                    'survey_done', 'budget_pending', 'budget_approved',
                    'worker_assigned', 'in_progress']
    ).count()

    # use aggregation to avoid N+1 queries per category/corp
    cat_label_map = dict(CATEGORY_CHOICES)
    cat_counts = (Complaint.objects.values('category')
                  .annotate(count=Count('id'))
                  .order_by('-count'))
    category_stats = [
        {'label': cat_label_map.get(row['category'], row['category']),
         'count': row['count'],
         'pct': round((row['count'] / total * 100) if total else 0)}
        for row in cat_counts if row['count']
    ]

    corp_name_map = dict(CITY_CORP_CHOICES)
    corp_counts = (Complaint.objects.values('city_corp')
                   .annotate(count=Count('id'))
                   .order_by('-count'))
    corp_stats = [
        {'code': row['city_corp'],
         'name': corp_name_map.get(row['city_corp'], row['city_corp']),
         'count': row['count']}
        for row in corp_counts if row['count']
    ]

    recent_resolved = Complaint.objects.filter(
        status__in=['resolved', 'closed']
    ).select_related('department').order_by('-updated_at')[:10]

    return render(request, 'complaints/public_dashboard.html', {
        'total': total,
        'resolved': resolved,
        'success_rate': success_rate,
        'open_count': open_count,
        'category_stats': category_stats,
        'corp_stats': corp_stats,
        'recent_resolved': recent_resolved,
    })


@login_required
def transfer_list(request):
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    status_f = request.GET.get('status', '')
    qs = ComplaintTransferRequest.objects.select_related(
        'complaint', 'from_department', 'to_department', 'requested_by'
    )
    if status_f:
        qs = qs.filter(status=status_f)
    return render(request, 'complaints/transfer_list.html', {
        'transfers': qs.order_by('-created_at'),
        'status_filter': status_f,
        'total': qs.count(),
    })


@login_required
def transfer_review(request, pk):
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    tr = get_object_or_404(ComplaintTransferRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve' and tr.status == 'pending':
            old_dept = tr.complaint.department
            with transaction.atomic():
                tr.complaint.department = tr.to_department
                tr.complaint.city_corp = tr.to_department.city_corp
                tr.complaint.save(update_fields=['department', 'city_corp', 'updated_at'])
                tr.status = 'approved'
                tr.reviewed_by = request.user
                tr.save()
                _log_event(tr.complaint, tr.complaint.status, request.user,
                           f'Transfer approved from {old_dept.name} to {tr.to_department.name}.',
                           'transfer_approved')
            # notifications outside the atomic block
            heads = User.objects.filter(role='admin', department=tr.to_department,
                                        is_active=True, is_department_head=True)
            notify_targets = heads if heads.exists() else User.objects.filter(
                role='admin', department=tr.to_department, is_active=True)
            for admin in notify_targets:
                _notify(admin, 'Complaint Transferred',
                        f'Complaint "{tr.complaint.title}" has been transferred to your department.',
                        'transfer_approved', tr.complaint)
            for admin in User.objects.filter(role='admin', department=old_dept, is_active=True):
                _notify(admin, 'Transfer Approved',
                        f'Transfer of "{tr.complaint.title}" to {tr.to_department.name} was approved.',
                        'transfer_approved', tr.complaint)
            _notify(tr.requested_by, 'Transfer Approved',
                    f'Your transfer request for "{tr.complaint.title}" was approved.',
                    'transfer_approved', tr.complaint)
            messages.success(request, 'Transfer approved.')

        elif action == 'reject' and tr.status == 'pending':
            reason = request.POST.get('rejection_reason', '').strip()
            with transaction.atomic():
                tr.status = 'rejected'
                tr.reviewed_by = request.user
                tr.rejection_reason = reason
                tr.save()
                _log_event(tr.complaint, tr.complaint.status, request.user,
                           f'Transfer to {tr.to_department.name} rejected. Reason: {reason}',
                           'transfer_rejected')
            _notify(tr.requested_by, 'Transfer Rejected',
                    f'Transfer request for "{tr.complaint.title}" was rejected. Reason: {reason}',
                    'transfer_rejected', tr.complaint)
            messages.warning(request, 'Transfer rejected.')

        return redirect('transfer_list')

    return render(request, 'complaints/transfer_review.html', {'tr': tr})


_COMMUNITY_PAGE_SIZE = 18
_PUBLIC_EVENT_TYPES = {'status_change', 'merged_as_primary', 'merged_as_duplicate'}


def community_list(request):
    # Browse all complaints without needing to log in.
    # Only public-safe fields are exposed.
    from departments.models import CITY_CORP_CHOICES

    qs = (
        Complaint.objects
        .select_related('department')
        .order_by('-created_at')
    )

    q        = request.GET.get('q', '').strip()
    cat_f    = request.GET.get('category', '').strip()
    status_f = request.GET.get('status', '').strip()
    corp_f   = request.GET.get('city_corp', '').strip()
    sort_f   = request.GET.get('sort', 'newest').strip()

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(location_text__icontains=q) |
            Q(description__icontains=q)
        )
    if cat_f and cat_f in dict(CATEGORY_CHOICES):
        qs = qs.filter(category=cat_f)
    if status_f and status_f in dict(STATUS_CHOICES):
        qs = qs.filter(status=status_f)
    if corp_f and corp_f in dict(CITY_CORP_CHOICES):
        qs = qs.filter(city_corp=corp_f)

    sort_map = {
        'newest':   '-created_at',
        'oldest':   'created_at',
        'updated':  '-updated_at',
    }
    qs = qs.order_by(sort_map.get(sort_f, '-created_at'))

    paginator = Paginator(qs, _COMMUNITY_PAGE_SIZE)
    try:
        page_obj = paginator.page(request.GET.get('page', 1))
    except InvalidPage:
        page_obj = paginator.page(1)

    return render(request, 'complaints/community_list.html', {
        'page_obj':         page_obj,
        'q':                q,
        'cat_f':            cat_f,
        'status_f':         status_f,
        'corp_f':           corp_f,
        'sort_f':           sort_f,
        'category_choices': CATEGORY_CHOICES,
        'status_choices':   STATUS_CHOICES,
        'corp_choices':     CITY_CORP_CHOICES,
        'total_count':      paginator.count,
    })


def community_detail(request, pk):
    # Public complaint detail — no login needed.
    # Identity, exact costs, internal notes, and finance data are kept private.
    complaint = get_object_or_404(
        Complaint.objects.select_related('department'),
        pk=pk,
    )

    # Strip internal notes and actor identity from the public timeline
    raw_history = (
        complaint.history
        .only('status', 'event_type', 'created_at')
        .order_by('created_at')
    )
    public_history = [
        {
            'status':         h.status,
            'status_display': h.get_status_display(),
            'event_type':     h.event_type,
            'created_at':     h.created_at,
        }
        for h in raw_history
        if h.event_type in _PUBLIC_EVENT_TYPES
    ]

    # Show a rough cost range instead of the exact surveyed amount
    survey_cost_range = None
    try:
        survey = complaint.survey_report  # OneToOne — raises if absent
        cost = float(survey.estimated_cost)
        if cost > 0:
            low  = round(cost * 0.70 / 1000) * 1000
            high = round(cost * 1.30 / 1000) * 1000
            survey_cost_range = (low, high)
    except Exception:
        pass

    if complaint.is_anonymous:
        reporter_label = complaint.anonymous_alias or 'Anonymous'
    else:
        reporter_label = 'Community Member'

    primary_complaint = None
    if complaint.is_duplicate and complaint.duplicate_of_id:
        primary_complaint = complaint.duplicate_of

    return render(request, 'complaints/community_detail.html', {
        'c':               complaint,
        'history':         public_history,
        'survey_cost_range': survey_cost_range,
        'reporter_label':  reporter_label,
        'progress':        complaint.get_status_progress(),
        'primary':         primary_complaint,
    })
