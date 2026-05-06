# CivicEye — Smart Civic Complaint & Transparency Management System

**University of Asia Pacific | Department of CSE | Course: CSE 314**
**Group: 02 | Section: C-1 | Semester: 3rd Year 2nd Semester**
**Submitted to:** Tanjina Helaly, Assistant Professor, CSE, UAP

---

## Team Members

| Name | ID | Role |
|---|---|---|
| Sujana Mahmuda Nite | 23101120 | Project Manager |
| Swagoto Utsab Sigha Roy | 23101124 | Developer |
| Nabiha Afrin | 23101125 | Architect & Tester |
| Mohammad Samir Hossain | 23101135 | Business Analyst |

---

## Overview

CivicEye is a web-based civic complaint management system for Bangladesh's city corporations. It transforms traditional manual complaint handling into a measurable, transparent, data-driven workflow.

Citizens report issues → Surveyors inspect → Budget approved → Field Workers or Technicians resolve → Citizens rate the resolution.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 4.x |
| Database | SQLite (dev) / MySQL (prod) |
| Frontend | Pure CSS (custom liquid glass system, no Bootstrap) |
| Auth | Django AbstractUser with RBAC |

---

## Features

- **Location auto-routing** — Types "Dhanmondi" → routes to DSCC automatically
- **6 role hierarchy** — Citizen, Surveyor, Field Worker, Technician, Dept Admin, Super Admin
- **Worker vs Technician** — Physical categories get Field Workers; electrical/IT get Technicians
- **Full timeline** — Every status change logged with actor and notes
- **Finance module** — Budget allocation, expense approval, budget progress bars
- **Notifications** — Every workflow event triggers targeted notifications
- **Dark/Light theme** — Server-side theme toggle, no JavaScript required

---

## City Corporations Supported

DNCC · DSCC · CCC · SCC · RCC · KCC · BCC · NCC · GCC · MCC

---

## Setup

```bash
# 1. Clone / extract project
cd civiceye_final

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install django pillow

# 4. Run migrations
python manage.py migrate

# 5. Seed departments and test accounts
python manage.py seed_data

# 6. Start server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Test Accounts (all passwords: Admin@123)

| Username | Role | Department |
|---|---|---|
| superadmin | Super Admin | All |
| admin_dscc | Department Admin | DSCC Roads & Infrastructure |
| surveyor1 | Surveyor | DSCC Roads & Infrastructure |
| worker1 | Field Worker | DSCC Roads & Infrastructure |
| tech1 | Technician | DSCC IT & Technology |
| citizen1 | Citizen | — |

---

## Role Guide

| Role | Can Do |
|---|---|
| **Citizen** | Submit complaints, track status, rate resolutions |
| **Surveyor** | Inspect assigned complaints, submit cost survey reports |
| **Field Worker** | Handle physical tasks (roads, water, sanitation, parks, fire, health, environment, building) |
| **Technician** | Handle technical tasks (electricity, transport, IT) |
| **Dept Admin** | Assign to surveyors, approve budgets, assign workers/technicians, manage dept users |
| **Super Admin** | Full system access, all city corps, Django admin, finance overview |

---

## Complaint Workflow

```
Citizen Submits
     ↓ (auto-routed to correct dept by location)
Dept Admin assigns Surveyor
     ↓
Surveyor inspects → submits cost estimate
     ↓ (auto-creates Expense)
Dept Admin approves budget
     ↓
Dept Admin assigns Field Worker OR Technician
     ↓
Worker updates status → Resolved
     ↓
Citizen rates resolution (1-5 stars)
```

---

## Project Structure

```
civiceye_final/
├── config/          # Django settings, URLs, context processors
├── accounts/        # Custom User model, auth, dashboard, profile
├── complaints/      # Complaint lifecycle, location router, survey
├── departments/     # Department model, city corps, seed data
├── finance/         # Budget allocation, expense approval
├── notifications/   # Per-user notification system
├── templates/       # Global base.html
└── manage.py
```
