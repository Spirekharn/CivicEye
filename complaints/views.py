from django.shortcuts import render, redirect
from .models import Complaint

def create_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        Complaint.objects.create(
            title=title,
            description=description,
            image=image
        )

        return redirect('/complaints/create/')

    return render(request, 'complaints/create.html')