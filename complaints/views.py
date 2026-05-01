from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Complaint
from analytics.models import DuplicateComplaint
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from departments.models import Department, Expense
from assignments.models import SurveyReport

User = get_user_model()


# complaint detail
def complaint_detail(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    return render(request, 'complaints/detail.html', {'complaint': complaint})


# complaint list
def complaint_list(request):
    query = request.GET.get('q')

    if query:
        complaints = Complaint.objects.filter(title__icontains=query)
    else:
        complaints = Complaint.objects.all()

    return render(request, 'complaints/list.html', {
        'complaints': complaints,
        'query': query
    })


# create complaint
def create_complaint(request):
    error = None

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        location_text = request.POST.get('location_text')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not title or not description:
            error = "Title and Description are required"
        else:
            # create complaint
            complaint = Complaint.objects.create(
                user=request.user,
                title=title,
                description=description,
                image=image,
                location_text=location_text,
                latitude=latitude or None,
                longitude=longitude or None,
                status='Pending'
            )

            # DUPLICATE DETECTION
            recent_time = timezone.now() - timedelta(hours=1)

            possible_duplicates = Complaint.objects.filter(
                title__icontains=title,
                location_text=location_text,
                created_at__gte=recent_time
            ).exclude(id=complaint.id)

            for dup in possible_duplicates:
                DuplicateComplaint.objects.create(
                    original=dup,
                    duplicate=complaint,
                    similarity_score=0.9
                )

            messages.success(request, "Complaint submitted successfully!")
            return redirect('/complaints/')

    return render(request, 'complaints/create.html', {'error': error})

# assign complaint
def assign_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id)


    users = User.objects.filter(role__in=['worker', 'admin'])

    if request.method == 'POST':
        user_id = request.POST.get('user')

        complaint.assigned_to_id = user_id
        complaint.status = 'In Progress'
        complaint.save()

        messages.success(request, "Complaint assigned successfully")
        return redirect('/complaints/')

    return render(request, 'complaints/assign.html', {
        'complaint': complaint,
        'users': users
    })

@login_required
def update_status(request, id, status):
    complaint = get_object_or_404(Complaint, id=id)

    # only worker/admin allowed
    if request.user.role not in ['worker', 'admin', 'superadmin']:
        return redirect('/')

    complaint.status = status
    complaint.save()

    messages.success(request, f"Status updated to {status}")
    return redirect('/complaints/')

@login_required
def assign_roles(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.user.role not in ['admin', 'superadmin']:
        return redirect('/')

    surveyors = User.objects.filter(role='surveyor')
    workers = User.objects.filter(role='worker')

    if request.method == 'POST':
        surveyor_id = request.POST.get('surveyor')
        worker_id = request.POST.get('worker')

        if surveyor_id:
            complaint.assigned_to_id = surveyor_id
            complaint.status = 'Assigned'
            complaint.save()

        if worker_id:
            complaint.assigned_to_id = worker_id
            complaint.status = 'In Progress'
            complaint.save()

        messages.success(request, "Roles assigned successfully")
        return redirect('/complaints/')

    return render(request, 'complaints/assign_roles.html', {
        'complaint': complaint,
        'surveyors': surveyors,
        'workers': workers
    })

@login_required
def approve_budget(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.user.role not in ['admin', 'superadmin']:
        return redirect('/')

    report = SurveyReport.objects.filter(complaint=complaint).first()

    if report:
        dept = Department.objects.first()  # simple mapping for demo

        if dept and dept.remaining_budget >= report.estimated_cost:
            dept.remaining_budget -= report.estimated_cost
            dept.save()

            Expense.objects.create(
                department=dept,
                complaint_id=complaint.id,
                amount=report.estimated_cost,
                description="Approved complaint expense"
            )

            complaint.status = 'In Progress'
            complaint.save()

            messages.success(request, "Budget approved and deducted")

    return redirect('/complaints/')