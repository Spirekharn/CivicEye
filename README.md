# CivicEye — Smart Civic Complaint & Transparency Management System

**University of Asia Pacific | Department of CSE | Course: CSE 314**
**Group: 02 | Section: C-1 | Semester: 3rd Year 2nd Semester**
**Submitted to:** Tanjina Helaly, Assistant Professor, CSE, UAP

---

## Team Members

| Name | ID | Role |
|---|---|---|
| Sujana Mahmuda Nite | 23101120 | Project Manager |
| Swagoto Utsab Singha Roy | 23101124 | Developer |
| Nabiha Afrin | 23101125 | Architect & Tester |

---

## Overview

CivicEye is a web-based civic complaint management system for Bangladesh's city corporations. It replaces manual, paper-based complaint handling with a fully transparent, measurable, and data-driven digital workflow.

Citizens report issues through a structured form. The system automatically routes each complaint to the correct city corporation department based on the location text. Surveyors inspect in the field, submit cost estimates, Finance Officers approve budgets, and Field Workers or Technicians carry out the work. Citizens follow every step in real time and rate the resolution when complete.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 4.x |
| Database | SQLite (development) / MySQL (production) |
| Frontend | Pure custom CSS (no Bootstrap, no frontend framework) |
| Auth | Django AbstractUser with role-based access control (RBAC) |
| Images | Pillow (evidence and completion photos) |

---

## Features

- **Location auto-routing** — Citizen types "Dhanmondi" or "Agrabad" in the location field and the complaint routes to the correct city corporation department automatically
- **8-role hierarchy** — Citizen, Surveyor, Field Worker, Technician, Dept Admin, Dept Head, Finance Officer, Super Admin
- **Worker vs Technician split** — Physical categories (roads, water, sanitation, parks, fire, health, environment, building) go to Field Workers; technical categories (electricity, transport, IT) go to Technicians
- **Department head designation** — Super Admin can designate any dept admin as department head; shown with a "Head" label throughout the system
- **Finance Officer role** — Dedicated role for reviewing expense requests and allocating department budgets system-wide
- **Complaint transfer system** — Dept Admin can request a transfer to another department with a reason; Super Admin reviews and approves or rejects
- **Auto-duplicate detection** — Complaints in the same category, within 500 m, submitted within 6 hours are automatically merged; the second citizen becomes a co-reporter on the primary complaint
- **Manual merge** — Admin can manually mark any complaint as a duplicate of another
- **Full status timeline** — Every status change, transfer event, and merge event is logged with actor, timestamp, and notes; transfer and merge events show distinct dot colors
- **Finance module** — Department budget allocation, expense approval with rejection reasons, fiscal year tracking, budget vs spent progress bars
- **Public stats dashboard** — Citizens can view aggregated system statistics (total complaints, resolution rate, breakdown by category and city corp) without seeing other citizens' personal data
- **Notifications** — Every workflow event triggers targeted in-app notifications for the relevant users
- **Hotline bar** — Emergency contact numbers (333 / 999) displayed on every page
- **Dark/Light theme** — Server-side theme toggle with no JavaScript required
- **Department accent dashboards** — Each department admin/head sees a dashboard with a colored left-border accent matching their department category
- **Citizen feedback and rating** — Resolved complaints can be rated 1–5 by the submitting citizen

---

## City Corporations Supported

| Code | Name |
|---|---|
| DNCC | Dhaka North City Corporation |
| DSCC | Dhaka South City Corporation |
| CCC | Chattogram City Corporation |
| KCC | Khulna City Corporation |
| RCC | Rajshahi City Corporation |
| BCC | Barishal City Corporation |
| SCC | Sylhet City Corporation |
| MCC | Mymensingh City Corporation |
| GCC | Gazipur City Corporation |
| NCC | Narayanganj City Corporation |
| COCC | Cumilla City Corporation |
| RNCC | Rangpur City Corporation |

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/Spirekharn/CivicEye.git
cd CivicEye

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install django pillow

# 4. Run migrations
python manage.py migrate

# 5. Seed departments and test accounts
python manage.py seed_data

# 6. Start the development server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Test Accounts

| Username | Password | Role | Department |
|---|---|---|---|
| SSNSTCE | SSNSTCE | Super Admin | All corps |
| finance_officer | Finance@123 | Finance Officer | System-wide |
| admin_dscc | Admin@123 | Dept Admin | DSCC Roads & Infrastructure |
| Swagoto | 23101124 | Citizen | — |
| qq | 123456 | Citizen | — |
| Labib | 23101128 | Surveyor | DSCC Roads & Infrastructure |
| Lamiya | 23101132 | Field Worker | DSCC Roads & Infrastructure |
| Sujan | 23101120 | Technician | DSCC IT & Technology |

---

## Role Guide

| Role | Responsibilities |
|---|---|
| **Citizen** | Submit complaints, track status in real time, view public stats, rate resolutions |
| **Surveyor** | View assigned complaint queue, conduct field inspections, submit survey reports with cost estimates |
| **Field Worker** | Handle physical repair tasks (roads, water, sanitation, parks, fire, health, environment, building) |
| **Technician** | Handle technical repair tasks (electricity, street lights, traffic signals, IT, CCTV) |
| **Dept Admin** | Assign surveyors, assign workers/technicians, request department transfers, perform manual merges |
| **Dept Head** | All dept admin capabilities; designated head of their department; receives incoming transfer notifications |
| **Finance Officer** | Review and approve or reject expense requests from survey reports; allocate annual budgets to departments; monitor system-wide spending |
| **Super Admin** | User management, department management, budget allocation, transfer request approval, system-wide reporting, Django admin access |

---

## Complaint Workflow

```
Citizen submits complaint (with location)
     |
     v (system auto-routes to correct dept by keyword)
Dept Admin assigns Surveyor
     |
     v
Surveyor inspects on-site, submits survey report with cost estimate
     |
     v (system auto-creates Expense record, notifies Finance Officer)
Finance Officer reviews and approves budget
     |
     v
Dept Admin assigns Field Worker OR Technician
     |       \
     |        v (if wrong department)
     |       Admin requests transfer → Super Admin reviews → approves or rejects
     |
     v
Worker updates status to In Progress → Resolved
     |
     v
Dept Admin closes complaint
     |
     v
Citizen rates resolution (1–5)
```

---

## Transfer Workflow

1. A Dept Admin finds the complaint belongs to another department
2. Admin opens the complaint and submits a Transfer Request (selects target department + reason)
3. Super Admin sees an alert on their dashboard and in the Transfer Requests list
4. Super Admin reviews and either approves (complaint.department changes, receiving dept notified) or rejects (reason required, requesting dept notified)
5. All transfer events appear in the complaint's status timeline

---

## Duplicate Detection

When a new complaint is submitted, the system checks for existing complaints with:
- Same category
- Location within 500 metres (Haversine formula)
- Submitted within the last 6 hours

If a match is found, the new complaint is flagged as a duplicate and the submitting citizen is added as a co-reporter on the primary complaint. Both citizens receive a notification.

---

## Project Structure

```
CivicEye/
├── config/          # Django settings, URL root, context processors
├── accounts/        # Custom User model, RBAC, dashboard, profile, about/FAQ pages
├── complaints/      # Complaint lifecycle, location router, survey, transfers, public dashboard
├── departments/     # Department model, 12 city corp choices, seed management command
├── finance/         # Budget allocation, expense approval, finance dashboard
├── notifications/   # Per-user in-app notification system
├── assignments/     # Surveyor and worker assignment records
├── analytics/       # Aggregated stats (used for public dashboard and superadmin panel)
├── templates/       # Global base.html with hotline bar and nav
└── manage.py
```
