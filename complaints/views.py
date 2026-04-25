from django.shortcuts import render, redirect
from .models import Complaint

def complaint_list(request):
    from .models import Complaint
    complaints = Complaint.objects.all()
    return render(request, 'complaints/list.html', {'complaints': complaints})

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
                title=title,
                description=description,
                image=image
            )
            return redirect('/complaints/')

    return render(request, 'complaints/create.html', {'error': error})