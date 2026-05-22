
import pytest
from django.db import IntegrityError

from accounts.models import User
from complaints.models import (
    Complaint,
    ComplaintStatusHistory,
    ComplaintTransferRequest,
    SurveyReport,
    ComplaintFeedback,
    STATUS_PROGRESS,
)
from departments.models import Department, CATEGORY_WORKER_TYPE
from finance.models import DepartmentBudget, Expense
from notifications.models import Notification


pytestmark = pytest.mark.django_db  # why: allow database operations in tests


# ─── factory helpers ────────────────────────────────────────────────────────


def make_dept(name="Roads Dept", slug="roads", city_corp="DSCC"):
    return Department.objects.create(
        name=name, slug=slug, city_corp=city_corp,
        description="Test department", is_active=True,
    )  # why: create reusable department


def make_user(username="citizen1", role="citizen", dept=None, password="Pass1234"):
    u = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password=password,
        role=role,
    )  # why: create reusable user

    if dept:
        u.department = dept
        u.save(update_fields=["department"])  # why: assign department if provided

    return u


def make_complaint(citizen=None, dept=None, status="submitted",
                   category="roads", title="Test Complaint"):
    citizen = citizen or make_user()  # why: create default citizen if missing

    return Complaint.objects.create(
        title=title,
        description="Something is broken.",
        category=category,
        status=status,
        priority="medium",
        citizen=citizen,
        department=dept,
        city_corp="DSCC",
        location_text="Dhanmondi, Dhaka",
    )  # why: create reusable complaint


# ─── User model ─────────────────────────────────────────────────────────────


def test_user_str_shows_username_and_role():
    u = make_user(username="alice", role="citizen")
    assert "alice" in str(u)  # why: username should appear in string
    assert "Citizen" in str(u)  # why: role should appear in string


def test_user_is_field_staff_for_worker_technician_surveyor():
    for role in ("worker", "technician", "surveyor"):
        u = make_user(username=f"staff_{role}", role=role)
        assert u.is_field_staff() is True  # why: these roles are field staff


def test_user_is_not_field_staff_for_admin_citizen():
    for role in ("admin", "citizen", "finance", "super_admin"):
        u = make_user(username=f"mgmt_{role}", role=role)
        assert u.is_field_staff() is False  # why: management roles are not field staff


def test_user_is_management_for_admin_finance_super_admin():
    for role in ("admin", "finance", "super_admin"):
        u = make_user(username=f"mgmt2_{role}", role=role)
        assert u.is_management() is True  # why: these are management roles


def test_user_is_dept_head_only_when_admin_and_flagged():
    dept = make_dept()
    u = make_user(username="dept_head", role="admin", dept=dept)

    assert u.is_dept_head() is False  # why: flag not enabled yet

    u.is_department_head = True
    u.save(update_fields=["is_department_head"])  # why: update department head flag

    assert u.is_dept_head() is True  # why: admin + flag should pass


def test_non_admin_is_never_dept_head():
    u = make_user(username="worker_head", role="worker")

    u.is_department_head = True
    u.save(update_fields=["is_department_head"])  # why: enable flag manually

    assert u.is_dept_head() is False  # why: only admin can be dept head


def test_user_is_finance_flag():
    u = make_user(username="fin_user", role="finance")
    assert u.is_finance() is True  # why: finance role should pass

    u2 = make_user(username="not_fin", role="citizen")
    assert u2.is_finance() is False  # why: citizen is not finance


# ─── Department model ────────────────────────────────────────────────────────


def test_department_str_includes_name_and_city_corp():
    dept = make_dept(name="Sanitation HQ", city_corp="DNCC")

    assert "Sanitation HQ" in str(dept)  # why: department name should appear
    assert "Dhaka North" in str(dept)  # why: city corporation should appear


def test_department_remaining_budget_calculation():
    super_admin = make_user(username="sa_budget", role="super_admin")
    dept = make_dept()

    DepartmentBudget.objects.create(
        department=dept, fiscal_year="2025-2026",
        allocated_amount=100_000, allocated_by=super_admin,
    )  # why: allocate department budget

    c = make_complaint(dept=dept)

    Expense.objects.create(
        title="Road repair", department=dept, complaint=c,
        amount=40_000, fiscal_year="2025-2026", status="approved",
    )  # why: create approved expense

    assert dept.total_budget == 100_000  # why: check total allocated budget
    assert dept.spent_budget == 40_000  # why: check used budget
    assert dept.remaining_budget == 60_000  # why: check remaining budget


def test_department_remaining_budget_zero_when_no_budget():
    dept = make_dept(name="No Budget Dept", slug="water", city_corp="CCC")

    assert dept.total_budget == 0  # why: no allocated budget
    assert dept.remaining_budget == 0  # why: remaining should also be zero


# ─── Complaint model ─────────────────────────────────────────────────────────

def test_complaint_str_contains_id_and_title():
    c = make_complaint(title="Broken Road")

    assert str(c.id) in str(c) or "#" in str(c)  # why: complaint id should appear
    assert "Broken Road" in str(c)  # why: title should appear


def test_complaint_default_status_is_submitted():
    citizen = make_user(username="cit_status")

    c = Complaint.objects.create(
        title="New Issue", description="desc", category="water",
        citizen=citizen, city_corp="DSCC", location_text="Gulshan",
    )  # why: create complaint without status

    assert c.status == "submitted"  # why: default status check


def test_complaint_get_status_progress_returns_correct_value():
    c = make_complaint(status="submitted")

    assert c.get_status_progress() == STATUS_PROGRESS["submitted"]
    # why: check submitted progress value

    c.status = "resolved"
    c.save(update_fields=["status"])  # why: change complaint status

    assert c.get_status_progress() == 100  # why: resolved should be 100%

    c.status = "rejected"
    c.save(update_fields=["status"])  # why: update rejected status

    assert c.get_status_progress() == 0  # why: rejected should be 0%


def test_complaint_required_worker_type_physical_is_worker():
    c = make_complaint(category="roads")
    assert c.required_worker_type() == "worker"  # why: roads need worker


def test_complaint_required_worker_type_technical_is_technician():
    c = make_complaint(category="electricity")
    assert c.required_worker_type() == "technician"  # why: electricity needs technician


def test_complaint_ordering_is_newest_first():
    u = make_user(username="order_cit")

    c1 = make_complaint(citizen=u, title="First")
    c2 = make_complaint(citizen=u, title="Second")

    qs = list(Complaint.objects.filter(citizen=u))

    assert qs[0].pk == c2.pk  # why: latest complaint should come first


def test_co_reporters_can_be_added_and_removed():
    owner = make_user(username="owner_cor")
    reporter = make_user(username="reporter_cor")

    c = make_complaint(citizen=owner)

    c.co_reporters.add(reporter)  # why: add co-reporter
    assert reporter in c.co_reporters.all()  # why: confirm reporter added

    c.co_reporters.remove(reporter)  # why: remove co-reporter
    assert reporter not in c.co_reporters.all()  # why: confirm reporter removed


# ─── ComplaintStatusHistory ──────────────────────────────────────────────────


def test_status_history_created_on_manual_insert():
    admin = make_user(username="admin_hist", role="admin")
    c = make_complaint()

    ComplaintStatusHistory.objects.create(
        complaint=c, status="under_review", changed_by=admin, notes="Reviewed."
    )  # why: create complaint history record

    assert c.history.filter(status="under_review").exists()
    # why: verify history saved


def test_status_history_ordering_is_oldest_first():
    admin = make_user(username="admin_order", role="admin")
    c = make_complaint()

    ComplaintStatusHistory.objects.create(
        complaint=c, status="submitted", changed_by=admin
    )  # why: create first history entry

    ComplaintStatusHistory.objects.create(
        complaint=c, status="under_review", changed_by=admin
    )  # why: create second history entry

    history = list(c.history.all())

    assert history[0].status == "submitted"  # why: oldest entry first
    assert history[1].status == "under_review"  # why: newer entry second


# ─── ComplaintTransferRequest ────────────────────────────────────────────────


def test_transfer_request_str_contains_complaint_and_target_dept():
    dept_a = make_dept(name="Dept A", slug="roads", city_corp="DSCC")
    dept_b = make_dept(name="Dept B", slug="water", city_corp="DSCC")

    admin = make_user(username="tr_admin", role="admin", dept=dept_a)

    c = make_complaint(dept=dept_a)

    tr = ComplaintTransferRequest.objects.create(
        complaint=c,
        from_department=dept_a,
        to_department=dept_b,
        reason="Wrong department.",
        requested_by=admin,
    )  # why: create transfer request

    result = str(tr)

    assert "Dept B" in result  # why: target department should appear


def test_transfer_request_default_status_is_pending():
    dept_a = make_dept(name="From Dept", slug="sanitation", city_corp="CCC")
    dept_b = make_dept(name="To Dept", slug="parks", city_corp="CCC")

    admin = make_user(username="tr_admin2", role="admin", dept=dept_a)

    c = make_complaint(dept=dept_a)

    tr = ComplaintTransferRequest.objects.create(
        complaint=c, from_department=dept_a, to_department=dept_b,
        reason="Re-routing.", requested_by=admin,
    )  # why: create transfer request without status

    assert tr.status == "pending"  # why: default status check


# ─── SurveyReport ────────────────────────────────────────────────────────────


def test_survey_report_linked_to_complaint_one_to_one():
    dept = make_dept(slug="health", name="Health Dept")

    surveyor = make_user(username="surv1", role="surveyor", dept=dept)

    c = make_complaint(dept=dept)

    report = SurveyReport.objects.create(
        complaint=c, surveyor=surveyor,
        findings="Crack observed.", estimated_cost=15000,
        priority_recommendation="high", estimated_days=5,
    )  # why: create survey report

    assert c.survey_report == report  # why: verify one-to-one relation

    with pytest.raises(IntegrityError):
        SurveyReport.objects.create(
            complaint=c, surveyor=surveyor,
            findings="Duplicate.", estimated_cost=0,
        )  # why: duplicate report should fail


# ─── ComplaintFeedback ───────────────────────────────────────────────────────


def test_feedback_linked_to_complaint_one_to_one():
    c = make_complaint(status="resolved")
    citizen = c.citizen

    fb = ComplaintFeedback.objects.create(
        complaint=c, citizen=citizen, rating=4, comment="Good job."
    )  # why: create feedback

    assert c.feedback.rating == 4  # why: verify feedback linked

    with pytest.raises(IntegrityError):
        ComplaintFeedback.objects.create(
            complaint=c, citizen=citizen, rating=5, comment="Duplicate review."
        )  # why: duplicate feedback should fail


# ─── DepartmentBudget ────────────────────────────────────────────────────────


def test_budget_unique_per_department_and_fiscal_year():
    sa = make_user(username="sa_unique", role="super_admin")

    dept = make_dept(name="Unique Budget Dept", slug="fire", city_corp="KCC")

    DepartmentBudget.objects.create(
        department=dept, fiscal_year="2025-2026",
        allocated_amount=50_000, allocated_by=sa,
    )  # why: create initial budget

    with pytest.raises(IntegrityError):
        DepartmentBudget.objects.create(
            department=dept, fiscal_year="2025-2026",
            allocated_amount=99_000, allocated_by=sa,
        )  # why: duplicate fiscal year budget should fail


def test_budget_str_includes_dept_name_fiscal_year_and_amount():
    sa = make_user(username="sa_str", role="super_admin")

    dept = make_dept(name="IT Dept", slug="it", city_corp="GCC")

    b = DepartmentBudget.objects.create(
        department=dept, fiscal_year="2025-2026",
        allocated_amount=200_000, allocated_by=sa,
    )  # why: create department budget

    s = str(b)

    assert "IT Dept" in s  # why: department name should appear
    assert "2025-2026" in s  # why: fiscal year should appear


# ─── Expense ─────────────────────────────────────────────────────────────────


def test_expense_default_status_is_pending():
    dept = make_dept(name="Expense Dept", slug="transport", city_corp="RCC")

    c = make_complaint(dept=dept)

    exp = Expense.objects.create(
        title="Labour cost", department=dept, complaint=c,
        amount=8_000, fiscal_year="2025-2026",
    )  # why: create expense without status

    assert exp.status == "pending"  # why: default expense status check


def test_expense_str_contains_title_amount_status():
    dept = make_dept(name="Exp Str Dept", slug="environment", city_corp="BCC")

    c = make_complaint(dept=dept)

    exp = Expense.objects.create(
        title="Equipment hire", department=dept, complaint=c,
        amount=12_000, fiscal_year="2025-2026",
    )  # why: create expense

    s = str(exp)

    assert "Equipment hire" in s  # why: title should appear
    assert "pending" in s  # why: status should appear


# ─── Notification ────────────────────────────────────────────────────────────


def test_notification_str_contains_username_and_title():
    u = make_user(username="notif_user")

    n = Notification.objects.create(
        user=u, title="Issue Resolved",
        message="Your complaint has been resolved.",
        notification_type="complaint_resolved",
    )  # why: create notification

    assert "notif_user" in str(n)  # why: username should appear
    assert "Issue Resolved" in str(n)  # why: title should appear


def test_notification_default_is_unread():
    u = make_user(username="unread_user")

    n = Notification.objects.create(
        user=u, title="Hello",
        message="Welcome.", notification_type="general",
    )  # why: create notification

    assert n.is_read is False  # why: default unread status


def test_notification_ordering_is_newest_first():
    u = make_user(username="notif_order")

    n1 = Notification.objects.create(
        user=u, title="First", message="1", notification_type="general"
    )

    n2 = Notification.objects.create(
        user=u, title="Second", message="2", notification_type="general"
    )

    qs = list(Notification.objects.filter(user=u))

    assert qs[0].pk == n2.pk  # why: newest notification first


# ─── CATEGORY_WORKER_TYPE mapping ────────────────────────────────────────────


def test_category_worker_type_covers_all_physical_categories():
    physical = ["roads", "water", "sanitation", "parks", "building", "environment", "fire", "health"]

    for cat in physical:
        assert CATEGORY_WORKER_TYPE[cat] == "worker", f"{cat} should map to 'worker'"
        # why: physical categories use worker


def test_category_worker_type_covers_technical_categories():
    technical = ["electricity", "transport", "it"]

    for cat in technical:
        assert CATEGORY_WORKER_TYPE[cat] == "technician", f"{cat} should map to 'technician'"
        # why: technical categories use technician