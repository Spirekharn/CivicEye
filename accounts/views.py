from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from .models import User
from departments.models import Department
from complaints.models import Complaint, ComplaintTransferRequest


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    stats = {
        'resolved':    Complaint.objects.filter(status__in=['resolved', 'closed']).count(),
        'total':       Complaint.objects.count(),
        'departments': Department.objects.filter(is_active=True).count(),
        'citizens':    User.objects.filter(role='citizen').count(),
    }
    return render(request, 'accounts/home.html', {'stats': stats})


def about_view(request):
    team = [
        {
            'name': 'Sujana Mahmuda Nite',
            'id': '23101120',
            'role': 'Project Manager',
            'abbr': 'SM',
            'url': None,
            'photo': None,
        },
        {
            'name': 'Swagoto Utsab Singha Roy',
            'id': '23101124',
            'role': 'Lead Developer',
            'abbr': 'SU',
            'url': 'https://spirekharn.github.io/SUSR_Portfolio/',
            'photo': 'accounts/img/swagoto.jpg',
        },
        {
            'name': 'Nabiha Afrin',
            'id': '23101125',
            'role': 'Architect & Tester',
            'abbr': 'NA',
            'url': None,
            'photo': None,
        },
    ]
    corps = [
        {'code': 'DNCC', 'name': 'Dhaka North City Corporation',  'area': 'Northern Dhaka'},
        {'code': 'DSCC', 'name': 'Dhaka South City Corporation',  'area': 'Southern Dhaka'},
        {'code': 'CCC',  'name': 'Chattogram City Corporation',   'area': 'Chattogram'},
        {'code': 'SCC',  'name': 'Sylhet City Corporation',       'area': 'Sylhet'},
        {'code': 'RCC',  'name': 'Rajshahi City Corporation',     'area': 'Rajshahi'},
        {'code': 'KCC',  'name': 'Khulna City Corporation',       'area': 'Khulna'},
        {'code': 'BCC',  'name': 'Barishal City Corporation',     'area': 'Barishal'},
        {'code': 'NCC',  'name': 'Narayanganj City Corporation',  'area': 'Narayanganj'},
        {'code': 'GCC',  'name': 'Gazipur City Corporation',      'area': 'Gazipur'},
        {'code': 'MCC',  'name': 'Mymensingh City Corporation',   'area': 'Mymensingh'},
        {'code': 'COCC', 'name': 'Cumilla City Corporation',      'area': 'Cumilla'},
        {'code': 'RNCC', 'name': 'Rangpur City Corporation',      'area': 'Rangpur'},
    ]
    milestones = [
        {'date': 'Feb 2026', 'title': 'Requirement Analysis',
         'desc': 'Surveyed 27 participants, conducted stakeholder interviews, documented functional and non-functional requirements aligned with city corporation workflows.'},
        {'date': 'Mar 2026', 'title': 'System Design',
         'desc': 'Designed MVT architecture, 7-entity ER diagram, department-aware complaint routing algorithm, and 6-role RBAC hierarchy.'},
        {'date': 'Apr 2026', 'title': 'Development',
         'desc': 'Built Django backend with 6 apps, Bangladesh location auto-router, finance module, notifications, and full role-scoped UI.'},
        {'date': 'May 2026', 'title': 'Testing & Delivery',
         'desc': 'Unit, integration, and UAT testing across all roles. Zero system errors. Documented and submitted to supervisor.'},
    ]
    categories = [
        {'name': 'Roads & Infrastructure'},
        {'name': 'Water & Sewerage'},
        {'name': 'Electricity & Street Lights'},
        {'name': 'Sanitation & Waste'},
        {'name': 'Parks & Recreation'},
        {'name': 'Public Health'},
        {'name': 'Building & Construction'},
        {'name': 'Transport & Traffic'},
        {'name': 'Environment & Drainage'},
        {'name': 'Fire & Emergency'},
        {'name': 'IT & Technology'},
        {'name': 'General Administration'},
    ]
    features = [
        {'icon': 'Loc', 'title': 'Smart Location Routing',
         'desc': 'Type any Bangladesh area — Dhanmondi, Agrabad, Sylhet — and the system auto-detects the city corporation and routes to the correct department.'},
        {'icon': 'Trk', 'title': 'End-to-End Tracking',
         'desc': 'Citizens follow every stage: submission, survey, budget approval, assignment, and resolution — with a full audit trail.'},
        {'icon': 'Rol', 'title': 'Right Person, Right Job',
         'desc': 'Physical issues go to Field Workers. Electrical and IT issues go to Technicians. Automatically filtered by complaint category.'},
        {'icon': 'Fin', 'title': 'Transparent Finance',
         'desc': 'Every expense links to a complaint. Department budgets are tracked, approved, and publicly auditable.'},
    ]
    workflow_steps = [
        {'title': 'Citizen submits complaint',
         'desc': 'Enters title, description, category, and location. System auto-detects city corporation and routes to the correct department.',
         'color': 'var(--pr)'},
        {'title': 'Admin reviews and assigns surveyor',
         'desc': 'Department admin reviews the complaint, sets priority, and assigns a surveyor from their department for on-site inspection.',
         'color': 'var(--t)'},
        {'title': 'Surveyor inspects on-site',
         'desc': 'Visits the location, documents findings, and submits a formal report with labour, equipment, and material cost estimates.',
         'color': 'var(--o)'},
        {'title': 'Finance officer reviews budget',
         'desc': 'Survey submission creates a pending expense automatically. Finance officer reviews against department budget and approves or rejects.',
         'color': 'var(--r)'},
        {'title': 'Right person assigned',
         'desc': 'System filters candidates by category type: physical issues show Field Workers only; technical issues show Technicians only.',
         'color': 'var(--br)'},
        {'title': 'Work begins on the ground',
         'desc': 'Worker or Technician marks the task in progress and can upload a completion photo as evidence when done.',
         'color': 'var(--s)'},
        {'title': 'Complaint resolved',
         'desc': 'Status changes to Resolved. Citizen receives an instant in-platform notification.',
         'color': 'var(--g)'},
        {'title': 'Citizen rates the resolution',
         'desc': 'Citizen submits a 1-5 star rating and written feedback. Ratings contribute to department performance metrics.',
         'color': 'var(--pr)'},
    ]
    return render(request, 'accounts/about.html', {
        'team': team,
        'corps': corps,
        'milestones': milestones,
        'categories': categories,
        'features': features,
        'workflow_steps': workflow_steps,
        'dept_count': Department.objects.filter(is_active=True).count(),
        'complaint_count': Complaint.objects.count(),
        'resolved_count': Complaint.objects.filter(status__in=['resolved', 'closed']).count(),
        'user_count': User.objects.count(),
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        fname    = request.POST.get('first_name', '').strip()
        lname    = request.POST.get('last_name', '').strip()
        phone    = request.POST.get('phone', '').strip()
        role     = request.POST.get('role', 'citizen')
        pw1      = request.POST.get('password1', '')
        pw2      = request.POST.get('password2', '')
        dept_id  = request.POST.get('department')
        VALID    = ['citizen', 'surveyor', 'worker', 'technician', 'admin']
        if role not in VALID:
            role = 'citizen'
        ctx = {
            'departments': Department.objects.filter(is_active=True).order_by('city_corp', 'name'),
            'post': request.POST,
        }
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/register.html', ctx)
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html', ctx)
        if pw1 != pw2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', ctx)
        if len(pw1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'accounts/register.html', ctx)
        user = User.objects.create_user(
            username=username, email=email, password=pw1,
            first_name=fname, last_name=lname, role=role, phone=phone,
        )
        if dept_id and role in ['surveyor', 'worker', 'technician', 'admin']:
            try:
                user.department = Department.objects.get(id=dept_id)
                user.save(update_fields=['department'])
            except Department.DoesNotExist:
                messages.warning(request, 'Selected department was not found, so the account was created without one.')
        login(request, user)
        messages.success(request, f'Welcome to CivicEye, {fname or username}!')
        return redirect('dashboard')
    return render(request, 'accounts/register.html', {
        'departments': Department.objects.filter(is_active=True).order_by('city_corp', 'name'),
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', ''),
        )
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('home')


@login_required
def dashboard_view(request):
    u = request.user
    if u.role == 'citizen':
        qs = Complaint.objects.filter(citizen=u)
        return render(request, 'accounts/dashboard.html', {
            'role_view': 'citizen',
            'complaints': qs.order_by('-created_at')[:8],
            'total': qs.count(),
            'resolved': qs.filter(status__in=['resolved', 'closed']).count(),
            'in_progress': qs.filter(status='in_progress').count(),
            'pending': qs.filter(status='submitted').count(),
        })

    elif u.role == 'surveyor':
        qs = Complaint.objects.filter(assigned_surveyor=u)
        return render(request, 'accounts/dashboard.html', {
            'role_view': 'surveyor',
            'complaints': qs.order_by('-created_at')[:8],
            'total': qs.count(),
            'pending': qs.filter(status__in=['assigned', 'surveying']).count(),
            'done': qs.filter(status='survey_done').count(),
        })

    elif u.role in ('worker', 'technician'):
        qs = Complaint.objects.filter(assigned_worker=u)
        return render(request, 'accounts/dashboard.html', {
            'role_view': u.role,
            'task_label': 'Field Tasks' if u.role == 'worker' else 'Technical Tasks',
            'complaints': qs.order_by('-updated_at')[:8],
            'total': qs.count(),
            'in_progress': qs.filter(status='in_progress').count(),
            'resolved': qs.filter(status='resolved').count(),
        })

    elif u.role == 'admin':
        if not u.department:
            return render(request, 'accounts/dashboard.html', {'role_view': 'admin_no_dept'})
        qs = Complaint.objects.filter(department=u.department)
        pending_transfers = ComplaintTransferRequest.objects.filter(
            from_department=u.department, status='pending'
        ).count()
        dept_slug = u.department.slug if u.department else ''
        return render(request, 'accounts/dashboard.html', {
            'role_view': 'admin',
            'complaints': qs.order_by('-created_at')[:10],
            'total': qs.count(),
            'pending': qs.filter(status__in=['submitted', 'under_review']).count(),
            'in_progress': qs.filter(status='in_progress').count(),
            'resolved': qs.filter(status__in=['resolved', 'closed']).count(),
            'dept': u.department,
            'dept_slug': dept_slug,
            'pending_transfers': pending_transfers,
        })

    elif u.role == 'finance':
        from finance.models import DepartmentBudget, Expense
        fiscal = '2025-2026'
        pending_expenses = Expense.objects.filter(status='pending').count()
        total_budget = DepartmentBudget.objects.filter(fiscal_year=fiscal).aggregate(
            Sum('allocated_amount'))['allocated_amount__sum'] or 0
        total_spent = Expense.objects.filter(fiscal_year=fiscal, status='approved').aggregate(
            Sum('amount'))['amount__sum'] or 0
        return render(request, 'accounts/dashboard.html', {
            'role_view': 'finance',
            'pending_expenses': pending_expenses,
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_budget - total_spent,
        })

    elif u.role == 'super_admin':
        all_c = Complaint.objects.all()
        pending_transfers = ComplaintTransferRequest.objects.filter(status='pending').count()
        return render(request, 'accounts/dashboard.html', {
            'role_view': 'super_admin',
            'complaints': all_c.order_by('-created_at')[:12],
            'total': all_c.count(),
            'pending': all_c.filter(status='submitted').count(),
            'in_progress': all_c.filter(status='in_progress').count(),
            'resolved': all_c.filter(status__in=['resolved', 'closed']).count(),
            'dept_count': Department.objects.filter(is_active=True).count(),
            'user_count': User.objects.count(),
            'cat_data': all_c.values('category').annotate(c=Count('id')).order_by('-c')[:6],
            'pending_transfers': pending_transfers,
        })

    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        u = request.user
        if request.POST.get('theme_only') == '1':
            new_theme = request.POST.get('theme', 'light')
            if new_theme in ('light', 'dark'):
                u.theme = new_theme
                u.save(update_fields=['theme'])
            return redirect(request.META.get('HTTP_REFERER') or 'dashboard')
        u.first_name = request.POST.get('first_name', u.first_name).strip()
        u.last_name  = request.POST.get('last_name',  u.last_name).strip()
        u.email      = request.POST.get('email',      u.email).strip()
        u.phone      = request.POST.get('phone',      u.phone).strip()
        u.address    = request.POST.get('address',    u.address).strip()
        theme = request.POST.get('theme', u.theme)
        if theme in ('light', 'dark'):
            u.theme = theme
        if request.FILES.get('profile_picture'):
            u.profile_picture = request.FILES['profile_picture']
        u.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'accounts/profile.html')


@login_required
def admin_users_view(request):
    if request.user.role not in ('admin', 'super_admin'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    role_f = request.GET.get('role', '')
    search = request.GET.get('q', '')
    users  = User.objects.all().order_by('-date_joined')
    if request.user.role == 'admin':
        users = users.filter(department=request.user.department)
    if role_f:
        users = users.filter(role=role_f)
    if search:
        users = users.filter(
            Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search)
        )
    return render(request, 'accounts/admin_users.html', {
        'users': users,
        'role_filter': role_f,
        'search': search,
        'roles': User.ROLE_CHOICES,
        'departments': Department.objects.filter(is_active=True).order_by('city_corp', 'name'),
    })


@login_required
def update_user_department(request, user_id):
    if request.user.role != 'super_admin':
        messages.error(request, 'Only Super Admin can allocate departments.')
        return redirect('admin_users')
    if request.method != 'POST':
        return redirect('admin_users')
    target = get_object_or_404(User, id=user_id)
    dept_id = request.POST.get('department', '')
    if dept_id:
        target.department = get_object_or_404(Department, id=dept_id, is_active=True)
    else:
        target.department = None
    target.save(update_fields=['department'])
    dept_name = target.department.name if target.department else 'No department'
    messages.success(request, f'Department updated for @{target.username}: {dept_name}.')
    return redirect('admin_users')


@login_required
def update_user_role(request, user_id):
    if request.user.role != 'super_admin':
        messages.error(request, 'Only Super Admin can change roles.')
        return redirect('admin_users')
    if request.method != 'POST':
        return redirect('admin_users')
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.warning(request, 'Cannot change your own role.')
        return redirect('admin_users')
    valid_roles = [r[0] for r in User.ROLE_CHOICES]
    new_role = request.POST.get('role', '')
    if new_role not in valid_roles:
        messages.error(request, 'Invalid role.')
        return redirect('admin_users')
    target.role = new_role
    if new_role != 'admin':
        target.is_department_head = False
    target.save(update_fields=['role', 'is_department_head'])
    messages.success(request, f'Role updated for @{target.username} to {new_role}.')
    return redirect('admin_users')


@login_required
def toggle_dept_head(request, user_id):
    if request.user.role != 'super_admin':
        messages.error(request, 'Only Super Admin can designate department heads.')
        return redirect('admin_users')
    if request.method != 'POST':
        return redirect('admin_users')
    target = get_object_or_404(User, id=user_id)
    if target.role != 'admin':
        messages.error(request, 'Only department admins can be designated as department heads.')
        return redirect('admin_users')
    target.is_department_head = not target.is_department_head
    target.save(update_fields=['is_department_head'])
    status = 'designated as department head' if target.is_department_head else 'removed as department head'
    messages.success(request, f'@{target.username} has been {status}.')
    return redirect('admin_users')


@login_required
def toggle_user_active(request, user_id):
    if request.user.role not in ('admin', 'super_admin'):
        return redirect('dashboard')
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.warning(request, 'Cannot deactivate yourself.')
        return redirect('admin_users')
    target.is_active = not target.is_active
    target.save()
    messages.success(request, f'User @{target.username} {"activated" if target.is_active else "deactivated"}.')
    return redirect('admin_users')


@login_required
def superadmin_dashboard(request):
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    from finance.models import DepartmentBudget, Expense
    all_c = Complaint.objects.all()
    pending_transfers = ComplaintTransferRequest.objects.filter(status='pending').count()
    return render(request, 'accounts/superadmin.html', {
        'all_complaints': all_c.count(),
        'pending': all_c.filter(status='submitted').count(),
        'in_progress': all_c.filter(status='in_progress').count(),
        'resolved': all_c.filter(status__in=['resolved', 'closed']).count(),
        'total_users': User.objects.count(),
        'total_depts': Department.objects.filter(is_active=True).count(),
        'total_budget': DepartmentBudget.objects.filter(fiscal_year='2025-2026').aggregate(
            Sum('allocated_amount'))['allocated_amount__sum'] or 0,
        'total_spent': Expense.objects.filter(fiscal_year='2025-2026', status='approved').aggregate(
            Sum('amount'))['amount__sum'] or 0,
        'recent_users': User.objects.order_by('-date_joined')[:8],
        'departments': Department.objects.filter(is_active=True).order_by('city_corp', 'name'),
        'corp_stats': all_c.values('city_corp').annotate(c=Count('id')).order_by('-c'),
        'all_complaints_qs': all_c,
        'pending_transfers': pending_transfers,
    })


def faq_view(request):
    return render(request, 'accounts/faq.html')


def contact_view(request):
    return render(request, 'accounts/contact.html')


def privacy_view(request):
    return render(request, 'accounts/privacy.html')


def terms_view(request):
    return render(request, 'accounts/terms.html')
