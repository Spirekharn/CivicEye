from django.shortcuts import render, redirect
from .forms import ComplaintForm
from django.contrib.auth.decorators import login_required

@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('/accounts/dashboard/')
    else:
        form = ComplaintForm()

    return render(request, 'complaints/create.html', {'form': form})