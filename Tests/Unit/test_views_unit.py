
import pytest
from django.urls import reverse

from accounts.models import User
from complaints.models import (
    Complaint,
    ComplaintStatusHistory,
    ComplaintTransferRequest,
    SurveyReport,
)
from departments.models import Department
from finance.models import DepartmentBudget, Expense
from notifications.models import Notification


pytestmark = pytest.mark.django_db


# ─── factory helpers ─────────────────────────────────────────────────────────

def make_dept(name="Roads Dept", slug="roads", city_corp="DSCC"):
    return Department.objects.create(
        name=name, slug=slug, city_corp=city_corp,
        description="Test dept", is_active=True,
    )


def make_user(username="user1", role="citizen", dept=None, password="Pass1234"):
    u = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password=password,
        role=role,
    )
    if dept:
        u.department = dept
        u.save(update_fields=["department"])
    return u


def make_complaint(citizen=None, dept=None, status="submitted",
                   category="roads", title="Test Complaint"):
    citizen = citizen or make_user(username="default_cit")
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
    )


# ─── Authentication / redirect views ─────────────────────────────────────────

def test_home_view_redirects_authenticated_user_to_dashboard(client):
    u = make_user(username="home_cit")
    client.force_login(u)
    response = client.get(reverse("home"))
    assert response.status_code == 302
    assert "dashboard" in response["Location"]


def test_home_view_renders_for_anonymous_user(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_login_view_get_returns_200(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200


def test_login_view_valid_credentials_redirects_to_dashboard(client):
    make_user(username="login_ok", password="Pass1234")
    response = client.post(reverse("login"), {
        "username": "login_ok",
        "password": "Pass1234",
    })
    assert response.status_code == 302
    assert "dashboard" in response["Location"]


def test_login_view_invalid_credentials_stays_on_login(client):
    make_user(username="login_bad", password="Pass1234")
    response = client.post(reverse("login"), {
        "username": "login_bad",
        "password": "WrongPassword",
    })
    assert response.status_code == 200  # re-renders login form


def test_logout_view_redirects_to_home(client):
    u = make_user(username="logout_user")
    client.force_login(u)
    response = client.post(reverse("logout"))
    assert response.status_code in (302, 301)


def test_register_view_creates_user_and_redirects(client):
    response = client.post(reverse("register"), {
        "username":   "brand_new",
        "email":      "brand_new@test.com",
        "first_name": "Brand",
        "last_name":  "New",
        "phone":      "01712345678",
        "role":       "citizen",
        "password1":  "StrongPass99",
        "password2":  "StrongPass99",
    })
    assert response.status_code == 302
    assert User.objects.filter(username="brand_new").exists()


def test_register_view_duplicate_username_stays_on_page(client):
    make_user(username="dup_register")
    response = client.post(reverse("register"), {
        "username":  "dup_register",
        "email":     "dup2@test.com",
        "role":      "citizen",
        "password1": "StrongPass99",
        "password2": "StrongPass99",
    })
    assert response.status_code == 200  # re-renders with error


# ─── Dashboard view ───────────────────────────────────────────────────────────

def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboard"))
    assert response.status_code == 302
    assert "login" in response["Location"]


def test_dashboard_citizen_renders(client):
    u = make_user(username="dash_cit")
    client.force_login(u)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


def test_dashboard_admin_renders_with_dept(client):
    dept  = make_dept()
    admin = make_user(username="dash_admin", role="admin", dept=dept)
    client.force_login(admin)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


def test_dashboard_surveyor_renders(client):
    dept     = make_dept(name="Surv Dept", slug="water", city_corp="CCC")
    surveyor = make_user(username="dash_surv", role="surveyor", dept=dept)
    client.force_login(surveyor)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


def test_dashboard_worker_renders(client):
    dept   = make_dept(name="Work Dept", slug="sanitation", city_corp="KCC")
    worker = make_user(username="dash_worker", role="worker", dept=dept)
    client.force_login(worker)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


def test_dashboard_finance_renders(client):
    finance = make_user(username="dash_fin", role="finance")
    client.force_login(finance)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


def test_dashboard_super_admin_renders(client):
    sa = make_user(username="dash_sa", role="super_admin")
    client.force_login(sa)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


# ─── Complaint list / create ──────────────────────────────────────────────────

def test_complaint_list_requires_login(client):
    response = client.get(reverse("complaint_list"))
    assert response.status_code == 302


def test_complaint_list_citizen_sees_own_complaints(client):
    citizen = make_user(username="list_cit")
    make_complaint(citizen=citizen, title="My Complaint")
    client.force_login(citizen)
    response = client.get(reverse("complaint_list"))
    assert response.status_code == 200
    assert b"My Complaint" in response.content


def test_complaint_create_get_returns_200_for_citizen(client):
    u = make_user(username="create_cit")
    client.force_login(u)
    response = client.get(reverse("complaint_create"))
    assert response.status_code == 200


def test_complaint_create_non_citizen_redirects(client):
    """Workers / admins should not be able to create complaints."""
    worker = make_user(username="worker_create", role="worker")
    client.force_login(worker)
    response = client.post(reverse("complaint_create"), {
        "title":         "Should Fail",
        "description":   "Worker trying to submit.",
        "category":      "roads",
        "location_text": "Dhaka",
        "priority":      "medium",
    })
    assert response.status_code == 302  # redirect away


def test_citizen_can_submit_complaint_and_status_history_created(client):
    dept    = make_dept(name="Roads DSCC", slug="roads", city_corp="DSCC")
    citizen = make_user(username="submit_cit")
    client.force_login(citizen)
    response = client.post(reverse("complaint_create"), {
        "title":         "Broken Footpath",
        "description":   "Footpath is broken near the park.",
        "category":      "roads",
        "location_text": "Dhanmondi, Dhaka",
        "priority":      "medium",
    })
    assert response.status_code == 302
    c = Complaint.objects.filter(title="Broken Footpath").first()
    assert c is not None
    assert c.status == "submitted"
    assert ComplaintStatusHistory.objects.filter(complaint=c, status="submitted").exists()


# ─── Complaint detail ─────────────────────────────────────────────────────────

def test_complaint_detail_visible_to_owner(client):
    citizen = make_user(username="detail_cit")
    c = make_complaint(citizen=citizen, title="My Detail Complaint")
    client.force_login(citizen)
    response = client.get(reverse("complaint_detail", args=[c.pk]))
    assert response.status_code == 200
    assert b"My Detail Complaint" in response.content


def test_complaint_detail_hidden_from_unrelated_citizen(client):
    owner   = make_user(username="owner_detail")
    intruder = make_user(username="intruder_detail")
    c = make_complaint(citizen=owner, title="Private Complaint")
    client.force_login(intruder)
    response = client.get(reverse("complaint_detail", args=[c.pk]))
    # Should redirect or return 403/404 — not 200
    assert response.status_code in (302, 403, 404)


def test_complaint_detail_visible_to_super_admin(client):
    citizen  = make_user(username="detail_sa_owner")
    sa       = make_user(username="sa_detail", role="super_admin")
    c = make_complaint(citizen=citizen, title="SA Visible Complaint")
    client.force_login(sa)
    response = client.get(reverse("complaint_detail", args=[c.pk]))
    assert response.status_code == 200


# ─── Admin assign complaint ───────────────────────────────────────────────────

def test_admin_can_assign_complaint_to_surveyor(client):
    dept     = make_dept(name="Assign Dept", slug="health", city_corp="DNCC")
    admin    = make_user(username="assign_admin",  role="admin",    dept=dept)
    surveyor = make_user(username="assign_surv",   role="surveyor", dept=dept)
    citizen  = make_user(username="assign_cit")
    c = make_complaint(citizen=citizen, dept=dept, status="submitted")
    client.force_login(admin)

    response = client.post(reverse("assign_complaint", args=[c.pk]), {
        "department": str(dept.pk),
        "surveyor":   str(surveyor.pk),
        "priority":   "high",
        "notes":      "",
    })
    c.refresh_from_db()
    assert response.status_code == 302
    assert c.status == "assigned"
    assert c.assigned_surveyor == surveyor
    assert Notification.objects.filter(user=surveyor).exists()
    assert Notification.objects.filter(user=citizen).exists()


def test_non_admin_cannot_access_assign_complaint(client):
    dept    = make_dept(name="No Assign", slug="parks", city_corp="RCC")
    citizen = make_user(username="noassign_cit")
    c = make_complaint(citizen=citizen, dept=dept)
    client.force_login(citizen)
    response = client.post(reverse("assign_complaint", args=[c.pk]), {
        "department": str(dept.pk),
    })
    assert response.status_code == 302
    c.refresh_from_db()
    assert c.assigned_surveyor is None


# ─── Assign worker ────────────────────────────────────────────────────────────

def test_admin_can_assign_worker_to_budget_approved_complaint(client):
    dept    = make_dept(name="Worker Dept", slug="building", city_corp="BCC")
    admin   = make_user(username="w_admin",   role="admin",  dept=dept)
    worker  = make_user(username="w_worker",  role="worker", dept=dept)
    citizen = make_user(username="w_citizen")
    c = make_complaint(citizen=citizen, dept=dept,
                       status="budget_approved", category="roads")
    client.force_login(admin)

    response = client.post(reverse("assign_worker", args=[c.pk]), {
        "worker": str(worker.pk),
        "notes":  "",
    })
    c.refresh_from_db()
    assert response.status_code == 302
    assert c.assigned_worker == worker
    assert c.status == "worker_assigned"
    assert Notification.objects.filter(user=worker).exists()
    assert Notification.objects.filter(user=citizen).exists()


# ─── Worker / surveyor update_status ─────────────────────────────────────────

def test_worker_can_mark_complaint_in_progress(client):
    dept    = make_dept(name="InProg Dept", slug="environment", city_corp="NCC")
    worker  = make_user(username="inprog_worker", role="worker", dept=dept)
    citizen = make_user(username="inprog_cit")
    c = make_complaint(citizen=citizen, dept=dept, status="worker_assigned")
    c.assigned_worker = worker
    c.save(update_fields=["assigned_worker"])
    client.force_login(worker)

    response = client.post(reverse("update_status", args=[c.pk]), {
        "status": "in_progress",
        "notes":  "Started work.",
    })
    c.refresh_from_db()
    assert response.status_code == 302
    assert c.status == "in_progress"


def test_worker_can_resolve_complaint_and_citizen_notified(client):
    dept    = make_dept(name="Resolve Dept", slug="fire", city_corp="GCC")
    worker  = make_user(username="resolve_worker", role="worker", dept=dept)
    citizen = make_user(username="resolve_cit")
    c = make_complaint(citizen=citizen, dept=dept, status="in_progress")
    c.assigned_worker = worker
    c.save(update_fields=["assigned_worker"])
    client.force_login(worker)

    response = client.post(reverse("update_status", args=[c.pk]), {
        "status": "resolved",
        "notes":  "Fixed the issue.",
    })
    c.refresh_from_db()
    assert response.status_code == 302
    assert c.status == "resolved"
    assert Notification.objects.filter(
        user=citizen, notification_type="complaint_resolved"
    ).exists()


def test_worker_cannot_change_status_of_unassigned_complaint(client):
    dept    = make_dept(name="NoAuth Dept", slug="it", city_corp="MCC")
    worker  = make_user(username="noauth_worker", role="worker", dept=dept)
    citizen = make_user(username="noauth_cit")
    c = make_complaint(citizen=citizen, dept=dept, status="worker_assigned")
    # assigned_worker is NOT set
    client.force_login(worker)

    response = client.post(reverse("update_status", args=[c.pk]), {
        "status": "in_progress",
    })
    c.refresh_from_db()
    assert c.status == "worker_assigned"  # unchanged


def test_admin_can_reject_complaint_and_citizen_notified(client):
    dept    = make_dept(name="Reject Dept", slug="transport", city_corp="COCC")
    admin   = make_user(username="rej_admin",   role="admin",   dept=dept)
    citizen = make_user(username="rej_citizen")
    c = make_complaint(citizen=citizen, dept=dept, status="under_review")
    client.force_login(admin)

    response = client.post(reverse("update_status", args=[c.pk]), {
        "status": "rejected",
        "notes":  "Outside jurisdiction.",
    })
    c.refresh_from_db()
    assert response.status_code == 302
    assert c.status == "rejected"
    assert Notification.objects.filter(user=citizen).exists()


# ─── Surveyor queue ───────────────────────────────────────────────────────────

def test_surveyor_queue_returns_200_for_surveyor(client):
    dept     = make_dept(name="Queue Dept", slug="water", city_corp="RNCC")
    surveyor = make_user(username="queue_surv", role="surveyor", dept=dept)
    client.force_login(surveyor)
    response = client.get(reverse("surveyor_queue"))
    assert response.status_code == 200


def test_non_surveyor_redirected_from_surveyor_queue(client):
    citizen = make_user(username="not_surv")
    client.force_login(citizen)
    response = client.get(reverse("surveyor_queue"))
    assert response.status_code == 302


# ─── Worker tasks ─────────────────────────────────────────────────────────────

def test_worker_tasks_returns_200_for_worker(client):
    dept   = make_dept(name="Task Dept", slug="sanitation", city_corp="SCC")
    worker = make_user(username="task_worker", role="worker", dept=dept)
    client.force_login(worker)
    response = client.get(reverse("worker_tasks"))
    assert response.status_code == 200


def test_citizen_redirected_from_worker_tasks(client):
    citizen = make_user(username="not_worker_cit")
    client.force_login(citizen)
    response = client.get(reverse("worker_tasks"))
    assert response.status_code == 302


# ─── Public dashboard ─────────────────────────────────────────────────────────

def test_public_dashboard_accessible_to_citizen(client):
    citizen = make_user(username="pub_cit")
    client.force_login(citizen)
    response = client.get(reverse("public_dashboard"))
    assert response.status_code == 200


def test_public_dashboard_redirects_non_citizen(client):
    admin = make_user(username="pub_admin", role="admin")
    client.force_login(admin)
    response = client.get(reverse("public_dashboard"))
    assert response.status_code == 302


# ─── Transfer review ──────────────────────────────────────────────────────────

def test_super_admin_can_approve_transfer_and_dept_updated(client):
    dept_a = make_dept(name="From Dept", slug="roads",    city_corp="DSCC")
    dept_b = make_dept(name="To Dept",   slug="water",    city_corp="DSCC")
    sa     = make_user(username="tr_sa",    role="super_admin")
    admin  = make_user(username="tr_admin", role="admin", dept=dept_a)
    citizen = make_user(username="tr_cit")
    c = make_complaint(citizen=citizen, dept=dept_a, status="under_review")

    tr = ComplaintTransferRequest.objects.create(
        complaint=c,
        from_department=dept_a,
        to_department=dept_b,
        reason="Re-routing needed.",
        requested_by=admin,
    )
    client.force_login(sa)

    response = client.post(reverse("transfer_review", args=[tr.pk]), {
        "action": "approve",
    })
    tr.refresh_from_db()
    c.refresh_from_db()
    assert response.status_code == 302
    assert tr.status == "approved"
    assert c.department == dept_b


def test_super_admin_can_reject_transfer(client):
    dept_a = make_dept(name="Rej From", slug="electricity", city_corp="DNCC")
    dept_b = make_dept(name="Rej To",   slug="parks",       city_corp="DNCC")
    sa     = make_user(username="rej_tr_sa", role="super_admin")
    admin  = make_user(username="rej_tr_adm", role="admin", dept=dept_a)
    citizen = make_user(username="rej_tr_cit")
    c = make_complaint(citizen=citizen, dept=dept_a)

    tr = ComplaintTransferRequest.objects.create(
        complaint=c, from_department=dept_a, to_department=dept_b,
        reason="Testing.", requested_by=admin,
    )
    client.force_login(sa)

    response = client.post(reverse("transfer_review", args=[tr.pk]), {
        "action":           "reject",
        "rejection_reason": "Not needed.",
    })
    tr.refresh_from_db()
    c.refresh_from_db()
    assert response.status_code == 302
    assert tr.status == "rejected"
    assert c.department == dept_a  # unchanged


def test_non_super_admin_cannot_access_transfer_review(client):
    dept_a = make_dept(name="N/A From", slug="health",   city_corp="KCC")
    dept_b = make_dept(name="N/A To",   slug="building", city_corp="KCC")
    admin  = make_user(username="trn_admin", role="admin", dept=dept_a)
    citizen = make_user(username="trn_cit")
    c = make_complaint(citizen=citizen, dept=dept_a)

    tr = ComplaintTransferRequest.objects.create(
        complaint=c, from_department=dept_a, to_department=dept_b,
        reason="Testing.", requested_by=admin,
    )
    client.force_login(admin)  # NOT super_admin

    response = client.post(reverse("transfer_review", args=[tr.pk]), {
        "action": "approve",
    })
    tr.refresh_from_db()
    assert tr.status == "pending"  # should not have changed


# ─── Admin users management ───────────────────────────────────────────────────

def test_super_admin_can_access_admin_users_page(client):
    sa = make_user(username="sa_users", role="super_admin")
    client.force_login(sa)
    response = client.get(reverse("admin_users"))
    assert response.status_code == 200


def test_citizen_cannot_access_admin_users_page(client):
    cit = make_user(username="cit_users")
    client.force_login(cit)
    response = client.get(reverse("admin_users"))
    assert response.status_code == 302


def test_super_admin_can_update_user_role(client):
    sa      = make_user(username="role_sa",  role="super_admin")
    target  = make_user(username="role_tgt", role="citizen")
    client.force_login(sa)

    response = client.post(
        reverse("update_user_role", args=[target.pk]),
        {"role": "worker"},
    )
    target.refresh_from_db()
    assert response.status_code == 302
    assert target.role == "worker"


def test_non_super_admin_cannot_update_user_role(client):
    admin  = make_user(username="role_admin_no", role="admin")
    target = make_user(username="role_tgt_no",   role="citizen")
    client.force_login(admin)

    response = client.post(
        reverse("update_user_role", args=[target.pk]),
        {"role": "worker"},
    )
    target.refresh_from_db()
    assert target.role == "citizen"  # unchanged


def test_super_admin_can_toggle_user_active(client):
    sa     = make_user(username="toggle_sa",  role="super_admin")
    target = make_user(username="toggle_tgt", role="citizen")
    assert target.is_active is True
    client.force_login(sa)

    response = client.post(reverse("toggle_user", args=[target.pk]))
    target.refresh_from_db()
    assert response.status_code == 302
    assert target.is_active is False


# ─── Profile view ─────────────────────────────────────────────────────────────

def test_profile_view_returns_200_for_authenticated_user(client):
    u = make_user(username="profile_cit")
    client.force_login(u)
    response = client.get(reverse("profile"))
    assert response.status_code == 200


def test_profile_view_updates_first_and_last_name(client):
    u = make_user(username="profile_update")
    client.force_login(u)

    response = client.post(reverse("profile"), {
        "first_name": "Updated",
        "last_name":  "Name",
        "email":      "profile_update@test.com",
        "phone":      "",
        "address":    "",
    })
    u.refresh_from_db()
    assert response.status_code == 302
    assert u.first_name == "Updated"
    assert u.last_name  == "Name"


# ─── Static / informational pages ────────────────────────────────────────────

def test_about_page_returns_200(client):
    response = client.get(reverse("about"))
    assert response.status_code == 200


def test_faq_page_returns_200(client):
    response = client.get(reverse("faq"))
    assert response.status_code == 200


def test_contact_page_returns_200(client):
    response = client.get(reverse("contact"))
    assert response.status_code == 200


def test_privacy_page_returns_200(client):
    response = client.get(reverse("privacy"))
    assert response.status_code == 200


def test_terms_page_returns_200(client):
    response = client.get(reverse("terms"))
    assert response.status_code == 200


# ─── Notification views ───────────────────────────────────────────────────────

def test_notification_list_returns_200_for_authenticated_user(client):
    u = make_user(username="notif_list_user")
    client.force_login(u)
    response = client.get(reverse("notification_list"))
    assert response.status_code == 200


def test_mark_read_marks_notification_as_read(client):
    u = make_user(username="mark_read_user")
    n = Notification.objects.create(
        user=u, title="Test", message="Test msg", notification_type="general"
    )
    assert n.is_read is False
    client.force_login(u)

    response = client.post(reverse("mark_read", args=[n.pk]))
    n.refresh_from_db()
    assert response.status_code in (302, 200)
    assert n.is_read is True


# ─── Department views ─────────────────────────────────────────────────────────

def test_department_list_returns_200(client):
    u = make_user(username="dept_list_user")
    client.force_login(u)
    response = client.get(reverse("department_list"))
    assert response.status_code == 200


def test_department_detail_returns_200_for_existing_dept(client):
    dept = make_dept(name="Detail Dept", slug="roads", city_corp="DSCC")
    u    = make_user(username="dept_det_user")
    client.force_login(u)
    response = client.get(reverse("department_detail", args=[dept.pk]))
    assert response.status_code == 200


def test_department_detail_returns_404_for_nonexistent(client):
    u = make_user(username="dept_404_user")
    client.force_login(u)
    response = client.get(reverse("department_detail", args=[99999]))
    assert response.status_code == 404
