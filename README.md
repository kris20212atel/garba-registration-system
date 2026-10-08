# Navratri Child Gift & Entry Management System

A complete **Django** web application to register children, manage daily attendance, and track gift distribution across a **20-day Navratri event**.

---

## Features

- **Registration**: Auto-generated IDs (`NAV001`–`NAV999`), photo upload, shared phone numbers allowed
- **Entry Verification**: Fast ID lookup with photo display, AJAX entry/gift buttons
- **Gift Distribution**: One gift per child per day with database-level duplicate protection
- **Dashboard**: Live stats for entries, gifts, and progress by day
- **Daily Reports**: Per-day attendance and gift table with export
- **Search**: Search by Registration ID, Name, or Phone (multiple results for shared phones)
- **20-Day History**: Complete per-child history preserved across all days
- **Excel Export**: 5 export types (children, today attendance, today gifts, all attendance, all gifts)
- **Day Management**: Switchable current day without data loss
- **Admin Login**: Secure Django authentication
- **24 Tests**: All critical business rules verified

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Seed Demo Data

```bash
python manage.py seed_demo
```

This creates:
- **Admin user**: `admin` / `navratri2026`
- **10 demo children** (NAV001–NAV010)
- **NAV001, NAV002, NAV003** share phone `9876543210` (demonstrating shared phone numbers)
- **3 days of attendance & gift history** (Days 1–3)
- **Current day set to Day 4**

### 4. Start the Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

Login with: `admin` / `navratri2026`

---

## Project Structure

```
navratri_app/
├── navratri_project/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── events/                  # Main application
│   ├── models.py            # Child, DailyAttendance, DailyGift, EventConfig
│   ├── views.py             # All views + API endpoints
│   ├── forms.py             # Registration and edit forms
│   ├── urls.py              # URL patterns
│   ├── admin.py             # Django admin
│   ├── context_processors.py
│   ├── tests.py             # 24 automated tests
│   └── management/
│       └── commands/
│           └── seed_demo.py # Demo data command
├── templates/
│   ├── base.html            # Base layout with navbar
│   ├── registration/
│   │   └── login.html
│   └── events/
│       ├── dashboard.html
│       ├── entry.html       # Entry & Gift Verification
│       ├── register.html
│       ├── registration_success.html
│       ├── child_list.html
│       ├── child_profile.html
│       ├── edit_child.html
│       ├── delete_child.html
│       ├── search.html
│       ├── daily_report.html
│       ├── event_settings.html
│       └── export.html
├── static/
│   └── css/
│       └── navratri.css     # Full theme CSS
├── media/                   # Uploaded photos (git-ignored)
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Business Rules Enforced

| Rule | Implementation |
|------|---------------|
| Unique Registration ID | `UNIQUE` DB constraint + auto-generation |
| Phone numbers NOT unique | No unique constraint on phone |
| One entry per child per day | `UniqueConstraint(child, event_day)` on DailyAttendance |
| One gift per child per day | `UniqueConstraint(child, event_day)` on DailyGift |
| Previous day does NOT block today | Checks only `event_day == current_day` |
| 20-day history preserved | Never deleted, stored per day |

---

## Running Tests

```bash
python manage.py test events --verbosity=2
```

**24 tests** covering all critical business rules:
- Registration ID uniqueness
- Phone number sharing
- Daily entry uniqueness (DB constraint)
- Daily gift uniqueness (DB constraint)
- Cross-day independence
- Complete NAV001 scenario (Day 1→20)
- API duplicate protection (409 responses)
- Search by shared phone number

---

## Admin Interface

Django admin is available at `/admin/`

Login: `admin` / `navratri2026`

---

## Environment Variables

Copy `.env.example` to `.env` and update for production:

```bash
cp .env.example .env
```

Key variables:
- `SECRET_KEY` — Change in production
- `DEBUG` — Set to `False` in production
- `ALLOWED_HOSTS` — Your domain name(s)

---

## Resetting Demo Data

To clear all data and re-seed:

```bash
python manage.py seed_demo --clear
```

---

## Technology Stack

- **Backend**: Django 6.x + Python 3.13
- **Database**: SQLite (development) — switchable to PostgreSQL/MySQL
- **Frontend**: Bootstrap 5 + Vanilla CSS + JavaScript
- **Fonts**: Google Fonts (Outfit)
- **Excel Export**: openpyxl
- **Image Upload**: Pillow
- **Auth**: Django built-in authentication
