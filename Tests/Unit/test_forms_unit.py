
import pytest

from accounts.forms import RegisterForm
from accounts.models import User
from complaints.forms import ComplaintForm
from departments.models import Department


pytestmark = pytest.mark.django_db  # why: enable database access in tests


# ─── factory helpers ─────────────────────────────────────────────────────────

def make_dept(name="Test Roads Dept", slug="roads", city_corp="DSCC"):
    return Department.objects.create(
        name=name, slug=slug, city_corp=city_corp, is_active=True
    )  # why: create reusable test department


# ─── RegisterForm ─────────────────────────────────────────────────────────────

def test_register_form_valid_citizen():
    form = RegisterForm(data={
        "username":  "newcitizen",
        "email":     "newcitizen@test.com",
        "role":      "citizen",
        "password1": "StrongPass99",
        "password2": "StrongPass99",
    })
    assert form.is_valid(), form.errors  # why: check valid citizen registration


def test_register_form_valid_worker_role():
    form = RegisterForm(data={
        "username":  "newworker",
        "email":     "newworker@test.com",
        "role":      "worker",
        "password1": "StrongPass99",
        "password2": "StrongPass99",
    })
    assert form.is_valid(), form.errors  # why: check valid worker registration


def test_register_form_rejects_mismatched_passwords():
    form = RegisterForm(data={
        "username":  "mismatch_user",
        "email":     "mm@test.com",
        "role":      "citizen",
        "password1": "Password123",
        "password2": "Different456",
    })
    assert form.is_valid() is False  # why: ensure mismatched passwords fail
    assert "password2" in form.errors  # why: confirm password field error


def test_register_form_rejects_missing_username():
    form = RegisterForm(data={
        "username":  "",
        "email":     "no_name@test.com",
        "role":      "citizen",
        "password1": "StrongPass99",
        "password2": "StrongPass99",
    })
    assert form.is_valid() is False  # why: username is required
    assert "username" in form.errors  # why: confirm username error exists


def test_register_form_rejects_duplicate_username():
    User.objects.create_user(username="existing_user", email="e@test.com", password="pass")
    # why: create existing user for duplicate check

    form = RegisterForm(data={
        "username":  "existing_user",
        "email":     "new@test.com",
        "role":      "citizen",
        "password1": "StrongPass99",
        "password2": "StrongPass99",
    })
    assert form.is_valid() is False  # why: duplicate username must fail
    assert "username" in form.errors  # why: confirm username duplication error


def test_register_form_rejects_invalid_role_choice():
    """The role field is a ChoiceField — any value outside ROLE_CHOICES must fail."""
    form = RegisterForm(data={
        "username":  "hacker",
        "email":     "h@test.com",
        "role":      "super_villain",  # not in ROLE_CHOICES  # why: invalid role test
        "password1": "StrongPass99",
        "password2": "StrongPass99",
    })
    assert form.is_valid() is False  # why: invalid role should fail
    assert "role" in form.errors  # why: confirm role field error


def test_register_form_rejects_weak_password():
    form = RegisterForm(data={
        "username":  "weakpassuser",
        "email":     "wp@test.com",
        "role":      "citizen",
        "password1": "123",
        "password2": "123",
    })
    assert form.is_valid() is False  # why: weak password must fail
    assert "password2" in form.errors or "password1" in form.errors
    # why: confirm password validation error


# ─── ComplaintForm ────────────────────────────────────────────────────────────

def test_complaint_form_valid_with_title_and_description():
    form = ComplaintForm(data={
        "title":       "Pothole on main road",
        "description": "Large pothole near school gate causing accidents.",
        "image":       None,
    })
    assert form.is_valid(), form.errors  # why: check valid complaint form


def test_complaint_form_rejects_empty_title():
    form = ComplaintForm(data={
        "title":       "",
        "description": "Some valid description here.",
    })
    assert form.is_valid() is False  # why: title cannot be empty
    assert "title" in form.errors  # why: confirm title field error


def test_complaint_form_rejects_empty_description():
    form = ComplaintForm(data={
        "title":       "Valid Title",
        "description": "",
    })
    assert form.is_valid() is False  # why: description cannot be empty
    assert "description" in form.errors  # why: confirm description error


def test_complaint_form_title_max_length_enforced():
    """Title field has max_length=200 on the model."""
    long_title = "A" * 201  # why: exceed max length limit

    form = ComplaintForm(data={
        "title":       long_title,
        "description": "Valid description.",
    })
    assert form.is_valid() is False  # why: long title should fail
    assert "title" in form.errors  # why: confirm title length error


def test_complaint_form_accepts_title_exactly_at_max_length():
    form = ComplaintForm(data={
        "title":       "B" * 200,  # why: test exact max length
        "description": "Valid description.",
    })
    assert form.is_valid(), form.errors  # why: max allowed length should pass


def test_complaint_form_only_exposes_allowed_fields():
    """ComplaintForm must not expose status, priority, department, or citizen fields."""
    form = ComplaintForm()
    allowed = {"title", "description", "image"}  # why: expected safe fields only
    assert set(form.fields.keys()) == allowed  # why: prevent restricted fields exposure