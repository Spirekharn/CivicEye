from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import RegisterForm

# STEP 4: Set up the custom user model reference
User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Registered successfully!")
            return redirect('login')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# TEMP DASHBOARDS
def citizen_dashboard(request):
    return render(request, 'accounts/dashboard.html')

def worker_dashboard(request):
    return HttpResponse("Worker Dashboard")

def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")

def about_view(request):
    return render(request, 'accounts/about.html')

def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')