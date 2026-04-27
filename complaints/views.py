from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Complaint

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