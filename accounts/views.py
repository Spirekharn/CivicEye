from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from complaints.models import Complaint
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required

User = get_user_model()


# register
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not username or not password or not role:
            messages.error(request, "All fields required")
            return redirect('register')

        try:
            User.objects.create_user(
                username=username,
                password=password,
                role=role
            )
        except IntegrityError:
            messages.error(request, "Username already exists")
            return redirect('register')

        messages.success(request, "Registered successfully")
        return redirect('login')

    return render(request, 'accounts/register.html')


# login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # role-based redirect
            if user.role == 'worker':
                return redirect('worker_dashboard')
            elif user.role == 'admin':
                return redirect('dashboard')
            elif user.role == 'superadmin':
                return redirect('/admin/')  # eita django admin
            else:
                return redirect('dashboard')

        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html')

# logout
def logout_view(request):
    logout(request)
    return redirect('login')


# dashboard
def dashboard_view(request):
    total = Complaint.objects.count()
    pending = Complaint.objects.filter(status='Pending').count()
    in_progress = Complaint.objects.filter(status='In Progress').count()
    resolved = Complaint.objects.filter(status='Resolved').count()

    context = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
    }

    return render(request, 'accounts/dashboard.html', context)


# home page
def home_view(request):
    total = Complaint.objects.count()
    pending = Complaint.objects.filter(status='Pending').count()
    in_progress = Complaint.objects.filter(status='In Progress').count()
    resolved = Complaint.objects.filter(status='Resolved').count()

    context = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
    }

    return render(request, 'accounts/home.html', context)


# citizen dashboard
def citizen_dashboard(request):
    return render(request, 'accounts/dashboard.html')


# worker dashboard
@login_required
def worker_dashboard(request):
    complaints = Complaint.objects.filter(assigned_to=request.user)

    return render(request, 'accounts/worker_dashboard.html', {
        'complaints': complaints
    })


# admin dashboard
def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")


# about
def about_view(request):
    return render(request, 'accounts/about.html')


# create superadmin
def create_superadmin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            try:
                User.objects.create_user(
                    username=username,
                    password=password,
                    role='superadmin'
                )
                messages.success(request, "Superadmin created")
                return redirect('login')
            except IntegrityError:
                messages.error(request, "Username exists")
                return redirect('create_superadmin')

    return render(request, 'accounts/superadmin.html')