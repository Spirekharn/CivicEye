# CivicEye — Smart Civic Complaint & Transparency Management System


---

## Team

| Name | Role |
|---|---|
| Sujana Mahmuda Nite | Project Manager |
| Swagoto Utsab Singha Roy | Lead Developer |
| Nabiha Afrin | Architect & Tester |

---


---

## What It Does

CivicEye is a web-based complaint management system built specifically for Bangladesh's 12 city corporations. Citizens report infrastructure and civic issues — broken roads, water supply failures, faulty street lights, garbage backlog — through a structured form. The system automatically routes each complaint to the correct city corporation department based on the citizen's location text, assigns the right personnel, tracks the full lifecycle with a 12-state workflow, links every repair to a departmental budget, and lets citizens follow every update in real time.

The goal is to replace ad-hoc phone calls and paper registers with a transparent, auditable, data-driven process.

---



| Page | Description |
|---|---|
| Home Page | System statistics, live complaint count, city corporation coverage |
| Complaint Form | Location field, category, anonymous option |
| Complaint Detail | 12-step progress bar, status timeline, hotline sidebar |
| Surveyor Queue | Assigned complaints with survey action buttons |
| Finance Dashboard | Department budget bars, pending expense list |
| Analytics Dashboard | Category pie, status doughnut, resolution trend, dept performance |
| Super Admin Panel | System-wide stats, transfer alerts, user management |

---

## Key Features

### Complaint Lifecycle (12 States)
Every complaint moves through a defined sequence: Submitted → Under Review → Assigned to Surveyor → Survey in Progress → Survey Complete → Budget Pending → Budget Approved → Worker Assigned → Work in Progress → Resolved → Closed. At any point the complaint can be Rejected. Every transition is logged with actor, timestamp, and notes.

### Location Auto-Routing
The citizen types a location in plain text — "Dhanmondi 27" or "Agrabad, Chattogram". The system matches this against an 80+ keyword dictionary covering all 12 city corporations and automatically routes the complaint to the correct department. No manual intervention needed for correctly named locations.

### Anonymous Complaints
Citizens can submit complaints anonymously. Their identity is never exposed on public pages. The system assigns an alias like "Anon #K7R2" for display. Super Admin retains oversight and can see the real identity for abuse prevention.

### Auto-Duplicate Detection (Haversine Algorithm)
When a new complaint is submitted with GPS coordinates, the system checks all complaints of the same category filed within the last 6 hours. If any existing complaint is within 500 metres (calculated using the Haversine formula), the new complaint is automatically flagged as a duplicate and the submitting citizen is added as a co-reporter on the primary complaint.

### Worker vs Technician Routing
Physical issues (roads, water, sanitation, parks, fire, health, environment, building) go to Field Workers. Technical issues (electricity, street lights, traffic systems, IT, CCTV) go to Technicians. The assignment page filters candidates automatically based on complaint category.

### Finance Module
Survey submission auto-creates a pending expense linked to the complaint. Finance Officers review expense requests against departmental budgets. The system blocks approval if the expense exceeds the remaining budget. All budgets are tracked per department per fiscal year (July–June). Citizens see a ±30% cost range; only admins and finance officers see the actual BDT breakdown.

### Transfer System
If a complaint arrives at the wrong department, the Dept Admin can request a transfer to another department with a written reason. Super Admin reviews and approves or rejects. The full transfer history appears in the complaint's event timeline with distinct colour coding.

### Community Transparency Dashboard
A publicly accessible dashboard lets any visitor browse complaints, filter by category, city corp, or status, and view complaint details — all without creating an account or logging in. No personal identity information, internal notes, or financial data is exposed on public pages.

### Analytics Dashboard (Admin, Finance, Super Admin)
Real-time aggregated charts powered by Chart.js showing: complaints by category, complaints by status, 30-day resolution trend, department performance rankings with average feedback ratings, surveyor and worker workload, budget utilisation by department, and monthly complaint volume by city corporation.

### In-App Notifications
Every workflow event — new complaint, surveyor assigned, survey submitted, budget approved, worker assigned, complaint resolved, transfer requested, duplicate detected — triggers targeted in-app notifications for the correct role. Notifications are not auto-cleared; users must explicitly mark them as read.

### Role-Based Access Control (7 Roles)
Each of the 7 roles has a dedicated dashboard and scoped access. Citizens see only their own complaints. Surveyors see only their assigned queue. Department Admins see only their department. Finance Officers see all budgets system-wide. Super Admin has unrestricted access.

---

## Roles

| Role | Responsibilities |
|---|---|
| **Citizen** | Submit complaints (regular or anonymous), track status, view public stats, rate resolution |
| **Surveyor** | Inspect assigned complaints, submit survey reports with cost estimates |
| **Field Worker** | Handle physical repair tasks; mark work in progress and resolved; upload completion photos |
| **Technician** | Handle technical tasks (electrical, IT, CCTV); same workflow as Field Worker |
| **Dept Admin** | Assign surveyors, assign workers, request transfers, manual merge duplicates, override status |
| **Finance Officer** | Approve/reject expense requests, allocate department budgets, view finance dashboard |
| **Super Admin** | Full system access; user management, department management, transfer approval, all analytics |

Department Admins can be designated as **Department Heads** by Super Admin. Department Heads receive priority notifications for incoming transfer requests.

---

## City Corporations Covered

| Code | Corporation | Area |
|---|---|---|
| DNCC | Dhaka North City Corporation | Northern Dhaka (Gulshan, Banani, Uttara, Mirpur) |
| DSCC | Dhaka South City Corporation | Southern Dhaka (Dhanmondi, Old Dhaka, Motijheel) |
| CCC | Chattogram City Corporation | Chattogram (Agrabad, Pahartali, Nasirabad) |
| SCC | Sylhet City Corporation | Sylhet |
| RCC | Rajshahi City Corporation | Rajshahi |
| KCC | Khulna City Corporation | Khulna |
| BCC | Barishal City Corporation | Barishal |
| NCC | Narayanganj City Corporation | Narayanganj |
| GCC | Gazipur City Corporation | Gazipur |
| MCC | Mymensingh City Corporation | Mymensingh |
| COCC | Cumilla City Corporation | Cumilla |
| RNCC | Rangpur City Corporation | Rangpur |

---

## Service Departments (per City Corporation)

Roads & Infrastructure · Water & Sewerage · Electricity & Street Lights · Sanitation & Waste · Environment & Drainage · Fire & Emergency · IT & Technology · Transport & Traffic

---

## How We Built It

We followed an iterative development approach over four months.

**Phase 1 — Requirement Analysis (Feb 2026)**
We surveyed stakeholders, mapped Bangladesh's city corporation governance structure, identified the 7 user roles, and documented functional requirements. Key early decisions: no third-party routing API (Bangladesh location data is not well covered), custom RBAC over Django groups, and a single unified complaint model with status as a finite state machine.

**Phase 2 — System Design (Mar 2026)**
Designed the database schema (7 core models, composite indexes, OneToOne relationships for survey reports and feedback). Designed the location router as a keyword dictionary with a configurable fallback. Chose to build the finance module tightly coupled to the complaint model so every expense links to a specific complaint. Chose Chart.js over a backend charting library to keep the server-side lightweight.

**Phase 3 — Development (Apr 2026)**
Built the Django backend incrementally — complaints first, then roles and dashboards, then finance, then analytics. All views are function-based with explicit role guards. No REST API (not required for scope). Custom CSS with CSS variables for light/dark theme without JavaScript framework dependency. Tom Select for searchable dropdowns on department and category fields.

**Phase 4 — Testing & Delivery (May 2026)**
Wrote 62 unit and integration tests covering all workflows (accounts, complaints, finance, analytics, community dashboard). Built Selenium end-to-end tests for the major user flows. Ran manual testing across all 7 roles with realistic demo data (23+ complaint scenarios seeded programmatically).

---

## What We Learned

**RBAC Design:** Getting role-scoped data access right required careful query design. Each view must enforce its own access checks rather than relying only on URL patterns. Finance officers needed read access to complaints without write access — this required a separate `_can_view_complaint` function.

**Workflow State Machines:** Encoding the 12-state lifecycle as a dict of allowed transitions per role prevented a large class of bugs where users could skip required steps (e.g., a worker resolving a complaint without first marking it in-progress).

**Performance:** The admin complaint list had N+1 query issues when stats were calculated from the already-filtered queryset. Splitting the base queryset (for stats) from the filtered queryset (for the displayed list) fixed this.

**Anonymous Identity:** Protecting citizen identity consistently requires a template tag, not just a template variable. The `display_reporter` template tag centralises the logic so it can't be accidentally bypassed in a new template.

**Database Indexes:** Adding composite indexes on `(status, department)`, `(city_corp, category)`, and `(citizen, status)` significantly reduced query time on the admin list view with large datasets.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 4.x |
| Database | SQLite (development) · MySQL-compatible (production) |
| Frontend | Custom CSS (no Bootstrap), vanilla JavaScript |
| Charts | Chart.js 4.x (CDN) |
| Dropdowns | Tom Select 2.3.x (CDN) |
| Auth | Django AbstractUser + custom RBAC |
| Images | Pillow |
| Geolocation | Haversine (pure Python, no external API) |
| Email | Django console backend (dev) · SMTP-ready (production) |
| Testing | Django TestCase (62 unit/integration tests) |
| Browser Testing | Selenium + webdriver-manager + pytest |

---

## Installation & Setup

```bash
# 1. Clone
git clone https://github.com/Spirekharn/CivicEye.git
cd CivicEye

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install django pillow

# 4. Apply database migrations
python manage.py migrate

# 5. Seed the 12 city corporations, 8 department types, and basic test accounts
python manage.py seed_data

# 6. (Optional) Load 23 realistic complaint scenarios across all workflow states
python manage.py create_demo_data

# 7. Start the development server
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

---

## Test Accounts

### Basic (from `seed_data`)

| Username | Password | Role |
|---|---|---|
| `SSNSTCE` | `SSNSTCE` | Super Admin |
| `finance_officer` | `Finance@123` | Finance Officer |
| `admin_dscc` | `Admin@123` | Dept Admin (DSCC Roads) |
| `Swagoto` | `23101124` | Citizen |
| `qq` | `123456` | Citizen |
| `Labib` | `23101128` | Surveyor (DSCC Roads) |
| `Lamiya` | `23101132` | Field Worker (DSCC Roads) |
| `Sujan` | `23101120` | Technician (DSCC IT) |

### Extended (from `create_demo_data`)

| Pattern | Password | Role |
|---|---|---|
| `mehedi_finance`, `nasrin_finance` | `Finance@2026` | Finance Officers |
| `rafiq_admin`, `taslima_admin`, `shabana_admin`, `karim_admin`, `reza_admin` | `Admin@2026` | Dept Admins |
| `labib_surveyor`, `sadia_surveyor`, `tamim_surveyor`, `mitu_surveyor`, `jahid_surveyor` | `Survey@2026` | Surveyors |
| `lamiya_worker`, `arif_worker`, `rokon_worker`, `sharmin_worker`, `mosharraf_worker` | `Worker@2026` | Field Workers |
| `sujan_tech`, `farida_tech`, `ripon_tech`, `shirin_tech`, `imran_tech` | `Tech@2026` | Technicians |
| `rahim_citizen` … `shiuly_citizen` (20 accounts) | `Citi@2026` | Citizens |

---

## Running Tests

```bash
# Unit and integration tests (62 tests, no browser needed)
python manage.py test

# Selenium end-to-end tests (requires Chrome + server running)
pip install selenium webdriver-manager pytest
python manage.py runserver &
pytest selenium/SeleniumPython/ -v
```

---

## Project Structure

```
CivicEye/
├── config/              Settings, URL root, context processors
├── accounts/            User model, RBAC, dashboard, profile, about/FAQ pages
├── complaints/          Complaint lifecycle, location router, survey, transfers,
│                        community dashboard, duplicate detection, template tags
├── departments/         Department model, 12 city corp choices, seed command
├── finance/             Budget allocation, expense approval, finance dashboard
├── notifications/       Per-user in-app notification system
├── analytics/           Aggregated charts — by category, status, trend, performance
├── templates/           Global base.html (hotline bar, nav, dark/light theme)
├── selenium/            End-to-end browser tests
│   └── SeleniumPython/  Test files, conftest, screenshots
└── manage.py
```

---

## Complaint Workflow

```
Citizen submits complaint (location text → auto-routed to correct dept)
    │
    ▼
Dept Admin reviews → assigns Surveyor
    │
    ▼
Surveyor inspects on-site → submits survey report with cost estimate
    │   (system auto-creates pending Expense, notifies Finance Officer)
    ▼
Finance Officer approves/rejects budget
    │
    ▼ (if approved)
Dept Admin assigns Field Worker or Technician
    │   (if wrong dept → request Transfer → Super Admin reviews)
    ▼
Worker marks In Progress → Resolved → uploads completion photo
    │
    ▼
Dept Admin closes complaint
    │
    ▼
Citizen rates resolution (1–5 stars)
```

---

## Future Improvements

**GIS / Mapping Integration**
Add a Leaflet.js or Google Maps embed to show complaint locations as pins and heatmaps. Citizens could tap a map to auto-fill GPS coordinates rather than typing location text.

**Mobile Application**
A React Native front-end consuming the Django backend via a REST API (Django REST Framework) would allow complaint submission with phone-camera evidence photos and real GPS auto-detection.

**External Authority Routing**
Route electricity complaints to DESCO/DPDC, water/drainage to WASA, and gas issues to Titas Gas directly through their respective APIs. The `FUTURE_AUTHORITIES` config block in `settings.py` is already prepared for this extension.

**SMS Notifications**
Integrate with Bangladesh telecom gateways (Grameenphone, Robi) to send SMS updates to citizens who do not have regular internet access.

**Location Inference**
Replace the keyword dictionary in `location_router.py` with an NLP model trained on Bangladesh geographic data so the system can handle spelling variants, transliteration from Bengali, and colloquial area names.

---

