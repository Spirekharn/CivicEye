from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Department
from accounts.models import User
from complaints.models import Complaint


@login_required
def department_list(request):
    depts = Department.objects.filter(is_active=True).order_by('city_corp', 'name')
    corps = sorted(set(d.city_corp for d in depts))
    return render(request, 'departments/list.html', {'departments': depts, 'corps': corps})


@login_required
def department_detail(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    staff = User.objects.filter(department=dept, is_active=True).order_by('role', 'first_name')
    complaint_count = Complaint.objects.filter(department=dept).count()
    resolved_count  = Complaint.objects.filter(department=dept, status__in=['resolved','closed']).count()
    return render(request, 'departments/detail.html', {
        'department': dept, 'staff': staff,
        'complaint_count': complaint_count,
        'resolved_count': resolved_count,
    })
