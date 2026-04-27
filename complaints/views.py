from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Complaint

User = get_user_model()

def complaint_detail(request, id):
    complaint = Complaint.objects.get(id=id)
    return render(request, 'complaints/detail.html', {'complaint': complaint})


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


def create_complaint(request):
    error = None

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if not title or not description:
            error = "Title and Description are required"
        else:
            Complaint.objects.create(
                user=request.user,
                title=title,
                description=description,
                image=image,
                status='Pending'
            )

            messages.success(request, "Complaint submitted successfully!")
            return redirect('/complaints/')

    return render(request, 'complaints/create.html', {'error': error})

def assign_complaint(request, id):
    complaint = Complaint.objects.get(id=id)
    users = User.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user')
        complaint.assigned_to_id = user_id
        complaint.status = 'In Progress'
        complaint.save()
        return redirect('/complaints/')

    return render(request, 'complaints/assign.html', {
        'complaint': complaint,
        'users': users
    })