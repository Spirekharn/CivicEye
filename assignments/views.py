from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from complaints.models import Complaint
from .models import SurveyReport


@login_required
def create_report(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.user.role != 'surveyor':
        return redirect('/')

    if request.method == 'POST':
        report = request.POST.get('report')
        cost = request.POST.get('cost')

        SurveyReport.objects.create(
            complaint=complaint,
            surveyor=request.user,
            report=report,
            estimated_cost=cost,
            verified=True
        )

        complaint.status = 'Verified'
        complaint.save()

        return redirect('/complaints/')

    return render(request, 'assignments/create_report.html', {
        'complaint': complaint
    })