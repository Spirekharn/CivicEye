from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import DepartmentBudget, Expense
from departments.models import Department
from accounts.models import User
from notifications.models import Notification
from complaints.models import Complaint


def _notify(user, title, msg, ntype, complaint=None):
    Notification.objects.create(user=user, title=title, message=msg,
                                 notification_type=ntype, complaint=complaint)


@login_required
def finance_dashboard(request):
    if request.user.role not in ('admin', 'super_admin'):
        messages.error(request, 'Access denied.'); return redirect('dashboard')
    u = request.user
    fiscal = '2025-2026'

    if u.role == 'admin':
        budgets = DepartmentBudget.objects.filter(fiscal_year=fiscal, department=u.department)
        pending = Expense.objects.filter(status='pending', department=u.department)
        expenses = Expense.objects.filter(fiscal_year=fiscal, department=u.department)
        depts = Department.objects.filter(id=u.department.id) if u.department else Department.objects.none()
    else:
        budgets = DepartmentBudget.objects.filter(fiscal_year=fiscal)
        pending = Expense.objects.filter(status='pending')
        expenses = Expense.objects.filter(fiscal_year=fiscal)
        depts = Department.objects.filter(is_active=True).order_by('city_corp', 'name')

    total_budget = budgets.aggregate(Sum('allocated_amount'))['allocated_amount__sum'] or 0
    total_spent  = expenses.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
    total_remaining = total_budget - total_spent

    dept_budgets = []
    for d in depts:
        b = DepartmentBudget.objects.filter(department=d, fiscal_year=fiscal).first()
        allocated = b.allocated_amount if b else 0
        spent = Expense.objects.filter(department=d, fiscal_year=fiscal, status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
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
    if request.user.role not in ('admin', 'super_admin'):
        return redirect('dashboard')
    if request.method == 'POST':
        dept_id = request.POST.get('department')
        fiscal  = request.POST.get('fiscal_year', '2025-2026').strip()
        amount  = request.POST.get('allocated_amount', 0)
        notes   = request.POST.get('notes', '').strip()
        try:
            dept   = Department.objects.get(id=dept_id)
            if request.user.role == 'admin' and dept != request.user.department:
                messages.error(request, 'You can only allocate budget for your own department.')
                return redirect('finance_dashboard')
            amount = float(amount)
            if amount <= 0: raise ValueError
            obj, created = DepartmentBudget.objects.update_or_create(
                department=dept, fiscal_year=fiscal,
                defaults={'allocated_amount': amount, 'allocated_by': request.user, 'notes': notes}
            )
            messages.success(request, f'Budget of BDT {amount:,.0f} allocated to {dept.name} for {fiscal}.')
            return redirect('finance_dashboard')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    depts = Department.objects.filter(is_active=True).order_by('city_corp', 'name')
    if request.user.role == 'admin' and request.user.department:
        depts = depts.filter(id=request.user.department.id)
    return render(request, 'finance/allocate.html', {'departments': depts})


@login_required
def expense_list(request):
    if request.user.role not in ('admin', 'super_admin'):
        return redirect('dashboard')
    if request.user.role == 'admin':
        expenses = Expense.objects.filter(department=request.user.department).select_related('department', 'complaint')
    else:
        expenses = Expense.objects.all().select_related('department', 'complaint')
    return render(request, 'finance/expense_list.html', {'expenses': expenses.order_by('-created_at')})


@login_required
def approve_expense(request, pk):
    if request.user.role not in ('admin', 'super_admin'):
        return redirect('dashboard')
    expense = get_object_or_404(Expense, pk=pk)
    if request.user.role == 'admin' and expense.department != request.user.department:
        messages.error(request, 'Access denied.')
        return redirect('finance_dashboard')
    action  = request.GET.get('action', 'approve')

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
        if expense.complaint:
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
        reason = request.GET.get('reason', 'Insufficient budget or invalid estimate.')
        expense.status = 'rejected'
        expense.rejection_reason = reason
        expense.approved_by = request.user
        expense.save()
        if expense.complaint:
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
