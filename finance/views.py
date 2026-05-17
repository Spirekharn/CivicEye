from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import DepartmentBudget, Expense, get_fiscal_year
from departments.models import Department
from accounts.models import User
from notifications.models import Notification


def _notify(user, title, msg, ntype, complaint=None):
    Notification.objects.create(user=user, title=title, message=msg,
                                 notification_type=ntype, complaint=complaint)


@login_required
def finance_dashboard(request):
    if request.user.role not in ('admin', 'finance', 'super_admin'):
        messages.error(request, 'Access denied.'); return redirect('dashboard')
    u = request.user
    fiscal = get_fiscal_year()

    if u.role == 'admin':
        budgets = DepartmentBudget.objects.filter(fiscal_year=fiscal, department=u.department)
        pending = Expense.objects.filter(status='pending', department=u.department)
        expenses = Expense.objects.filter(fiscal_year=fiscal, department=u.department)
        depts = Department.objects.filter(id=u.department.id) if u.department else Department.objects.none()
    else:
        # finance and super_admin see everything
        budgets = DepartmentBudget.objects.filter(fiscal_year=fiscal)
        pending = Expense.objects.filter(status='pending')
        expenses = Expense.objects.filter(fiscal_year=fiscal)
        depts = Department.objects.filter(is_active=True).order_by('city_corp', 'name')

    total_budget = budgets.aggregate(Sum('allocated_amount'))['allocated_amount__sum'] or 0
    total_spent  = expenses.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
    total_remaining = total_budget - total_spent

    # build lookup maps in 2 queries instead of 2×N queries
    budget_map = {b.department_id: b.allocated_amount
                  for b in DepartmentBudget.objects.filter(fiscal_year=fiscal)}
    spent_map = {
        row['department']: row['total']
        for row in Expense.objects.filter(fiscal_year=fiscal, status='approved')
                                  .values('department')
                                  .annotate(total=Sum('amount'))
    }
    dept_budgets = []
    for d in depts:
        allocated = budget_map.get(d.pk, 0)
        spent = spent_map.get(d.pk, 0) or 0
        remaining = max(0, allocated - spent)
        pct = min(100, round((spent / allocated * 100) if allocated else 0))
        dept_budgets.append({'dept': d, 'allocated': allocated, 'spent': spent, 'remaining': remaining, 'pct': pct})

    return render(request, 'finance/dashboard.html', {
        'fiscal_year': fiscal,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_remaining': total_remaining,
        'pending_expenses': pending.select_related('department', 'complaint'),
        'dept_budgets': dept_budgets,
    })


@login_required
def allocate_budget(request):
    if request.user.role not in ('finance', 'super_admin'):
        messages.error(request, 'Only Finance Officers can allocate budgets.')
        return redirect('dashboard')
    depts = Department.objects.filter(is_active=True).order_by('city_corp', 'name')
    if request.method == 'POST':
        dept_id = request.POST.get('department')
        fiscal  = request.POST.get('fiscal_year', get_fiscal_year()).strip()
        amount  = request.POST.get('allocated_amount', 0)
        notes   = request.POST.get('notes', '').strip()
        try:
            dept = Department.objects.get(id=dept_id)
        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')
            return render(request, 'finance/allocate.html', {
                'departments': depts, 'current_fiscal_year': get_fiscal_year()})
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError('Amount must be greater than zero.')
        except (TypeError, ValueError) as exc:
            messages.error(request, f'Invalid budget amount: {exc}')
            return render(request, 'finance/allocate.html', {
                'departments': depts, 'current_fiscal_year': get_fiscal_year()})
        DepartmentBudget.objects.update_or_create(
            department=dept, fiscal_year=fiscal,
            defaults={'allocated_amount': amount, 'allocated_by': request.user, 'notes': notes}
        )
        messages.success(request, f'Budget of BDT {amount:,.0f} allocated to {dept.name} for {fiscal}.')
        return redirect('finance_dashboard')

    return render(request, 'finance/allocate.html', {
        'departments': depts,
        'current_fiscal_year': get_fiscal_year(),
    })


@login_required
def expense_list(request):
    if request.user.role not in ('admin', 'finance', 'super_admin'):
        return redirect('dashboard')
    if request.user.role == 'admin':
        expenses = Expense.objects.filter(department=request.user.department).select_related('department', 'complaint')
    else:
        expenses = Expense.objects.all().select_related('department', 'complaint')
    return render(request, 'finance/expense_list.html', {'expenses': expenses.order_by('-created_at')})


@login_required
def approve_expense(request, pk):
    if request.user.role not in ('finance', 'super_admin'):
        messages.error(request, 'Only Finance Officers can approve or reject expenses.')
        return redirect('finance_dashboard')
    expense = get_object_or_404(Expense, pk=pk)
    action = request.POST.get('action', 'approve')

    if expense.status != 'pending':
        messages.error(request, 'This expense has already been reviewed.')
        return redirect('finance_dashboard')

    if action == 'approve':
        spent = Expense.objects.filter(
            department=expense.department,
            fiscal_year=expense.fiscal_year,
            status='approved',
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        budget = DepartmentBudget.objects.filter(
            department=expense.department,
            fiscal_year=expense.fiscal_year,
        ).first()
        allocated = budget.allocated_amount if budget else 0
        if expense.amount > allocated - spent:
            messages.error(request, 'Insufficient remaining department budget for this expense.')
            return redirect('finance_dashboard')
        expense.status = 'approved'
        expense.approved_by = request.user
        expense.save()
        if expense.complaint and expense.complaint.status == 'budget_pending':
            c = expense.complaint
            c.status = 'budget_approved'
            c.save()
            from complaints.models import ComplaintStatusHistory
            ComplaintStatusHistory.objects.create(
                complaint=c, status='budget_approved', changed_by=request.user,
                notes=f'Budget of BDT {expense.amount:,.0f} approved by {request.user.get_full_name()}.')
            _notify(c.citizen, 'Budget Approved', f'Budget approved for your complaint "{c.title}". A worker will be assigned soon.', 'budget_approved', c)
        messages.success(request, f'Expense of BDT {expense.amount:,.0f} approved.')
    elif action == 'reject':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            reason = 'Insufficient budget or invalid estimate.'
        expense.status = 'rejected'
        expense.rejection_reason = reason
        expense.approved_by = request.user
        expense.save()
        if expense.complaint and expense.complaint.status == 'budget_pending':
            c = expense.complaint
            c.status = 'rejected'
            c.save()
            from complaints.models import ComplaintStatusHistory
            ComplaintStatusHistory.objects.create(
                complaint=c, status='rejected', changed_by=request.user,
                notes=f'Budget rejected: {reason}')
            _notify(c.citizen, 'Budget Rejected', f'Budget for your complaint "{c.title}" was rejected. Reason: {reason}', 'budget_rejected', c)
        messages.warning(request, 'Expense rejected.')

    return redirect('finance_dashboard')
