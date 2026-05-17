# CivicEye Selenium Test Suite

End-to-end browser tests for the CivicEye complaint management system.

## Prerequisites

1. Python 3.9+
2. Google Chrome (any recent version)
3. The following packages:

```
pip install selenium webdriver-manager pytest
```

4. CivicEye server running locally with seed data loaded:

```
python manage.py seed_data
python manage.py create_demo_data   # optional — adds richer demo scenarios
python manage.py runserver
```

## Running the Tests

From the project root:

```bash
# Run all Selenium tests
pytest selenium/SeleniumPython/ -v

# Run with visible browser window (default)
pytest selenium/SeleniumPython/ -v

# Run headless (no browser window — useful for CI/recording)
pytest selenium/SeleniumPython/ -v --headless

# Save a screenshot when a test fails
pytest selenium/SeleniumPython/ -v --screenshots

# Run only one test file
pytest selenium/SeleniumPython/test_login.py -v

# Run a single test
pytest selenium/SeleniumPython/test_login.py::test_valid_login_redirects_to_dashboard -v
```

## Test Files

| File | What it covers |
|---|---|
| `test_login.py` | Login, logout, invalid credentials, role-based redirect |
| `test_logout.py` | Sign-out behaviour, theme toggle, dark mode persistence |
| `test_register.py` | Registration form validation, duplicate username, short password |
| `test_complaint.py` | Complaint submission, anonymous reporting, access control |
| `test_community.py` | Public community dashboard, privacy, filters, detail page |
| `test_workflow.py` | Admin list, surveyor queue, worker tasks, notifications, profile |
| `test_finance.py` | Finance dashboard, analytics, API endpoints, access gates |

## Configuration

The tests connect to `http://127.0.0.1:8000` by default.
To use a different URL:

```bash
CIVICEYE_TEST_URL=http://localhost:8080 pytest selenium/SeleniumPython/ -v
```

## Test Accounts Used

| Account | Role |
|---|---|
| `Swagoto` / `23101124` | Citizen |
| `qq` / `123456` | Citizen |
| `Labib` / `23101128` | Surveyor |
| `Lamiya` / `23101132` | Field Worker |
| `Sujan` / `23101120` | Technician |
| `admin_dscc` / `Admin@123` | Dept Admin (DSCC Roads) |
| `finance_officer` / `Finance@123` | Finance Officer |
| `SSNSTCE` / `SSNSTCE` | Super Admin |

All accounts are created by `python manage.py seed_data`.
