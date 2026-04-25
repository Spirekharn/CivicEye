from django.shortcuts import render, redirect
from .models import Complaint

def complaint_detail(request, id):
    from .models import Complaint
    complaint = Complaint.objects.get(id=id)
    return render(request, 'complaints/detail.html', {'complaint': complaint})

def complaint_list(request):
    from .models import Complaint

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
                title=title,
                description=description,
                image=image
            )
            return redirect('/complaints/')

    return render(request, 'complaints/create.html', {'error': error})