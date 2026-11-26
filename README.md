# HMS — Hospital Management System

A web-based Hospital Management System built with Django, designed for a small
hospital running on a local area network (LAN). It covers the full patient
journey: registration, OPD queue, consultations, lab/pharmacy orders, inpatient
care, nursing documentation, and billing.

## 1. Problem & Solution

### The problem

Hospitals and clinics often run on paper files or disconnected tools. This
causes:

- **Lost or duplicated patient records** — same patient registered multiple
  times, allergies and history missed.
- **No visibility of the queue** — patients don't know wait times; staff can't
  see bottlenecks.
- **Untracked clinical workflow** — vitals, orders, results, and medications
  live in different books; nothing links them to one visit.
- **Billing leakage** — services rendered are not always charged; invoices are
  prepared manually at the end.
- **No audit trail** — medico-legal disputes can't be reconstructed.
- **Unauthorized access** — anyone with a file can see any patient's data.

### The solution

HMS replaces the paper trail with a single system where:

- Every patient gets a **permanent MRN**; registration searches first to avoid
  duplicates.
- Every visit is an **Encounter** moving through a defined state machine
  (check-in → vitals → queue → consult → orders → disposition), so nothing is
  "lost between departments".
- Every clinical action (vitals, notes, orders, medication administration) is
  recorded against the encounter with **who, what, when** — immutable audit log.
- Every billable event automatically writes a **charge**; the invoice is just a
  grouped view of charges.
- **Role-based + object-level permissions** control exactly who sees what —
  a nurse sees her ward's patients, a receptionist sees registration only.
- **Single session per user** and **login lockout** protect shared workstations.

## 2. Functionality & Non-Functionality

### Functional requirements

| Area | Features |
|---|---|
| Patients | Register/search by MRN, name, phone, NHIS, national ID; demographics, next-of-kin, blood group; paginated lists |
| OPD flow | Check-in → vitals → queue token → doctor assignment → consult (SOAP + ICD-10) → orders (lab/meds/procedures) → disposition |
| Queue timers | OPD patients auto-leave queue 24h after diagnosis; detained patients observed max 24h |
| Inpatient | Wards, beds, admission, ward rounds, discharge |
| Nursing | Care notes, medication administration record (MAR), procedure logs |
| Lab/Pharmacy | Order → result → verify → dispense workflow; stock tracking |
| Billing | Charge ledger, tariffs, invoices, payments, receipts (printable) |
| Reports | Census, revenue, occupancy dashboards |
| Security | Login (username or email), axes lockout after 3 failures, one active session per user, role + object permissions, full audit log |

### Non-functional requirements

- **Performance**: pages < 500 ms on LAN hardware; SQLite now, PostgreSQL-ready.
- **Data safety**: immutable clinical records, audit log on all clinical/financial actions, soft-delete policy.
- **Availability**: runs on one LAN server; nightly DB backup script (planned).
- **Usability**: keyboard-friendly forms, print-first templates (invoices, wristbands, lab reports), HTMX partial updates without page reloads.
- **Maintainability**: strict lint (ruff), type checking (mypy + django-stubs), pytest suite.
- **Security**: session auth, per-role permissions, guardian object-level ACLs, brute-force protection.

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5.2 (server-rendered, monolith) |
| UI | Django templates + HTMX + vanilla CSS |
| Database | SQLite (dev) → PostgreSQL (production, env switch) |
| Auth | Django auth, username-or-email backend |
| Authorization | django-guardian (object perms) + group roles + custom decorators |
| Brute-force protection | django-axes (lockout after 3 failures) |
| Config | python-decouple (`.env`) |
| Testing | pytest + pytest-django |
| Lint/Types | ruff (strict), mypy + django-stubs |
| Package manager | uv (`pyproject.toml`) |

## 4. Deployment

Target: one Windows/Linux machine on the hospital LAN running the Django app;
staff access it via browser at `http://<server-ip>:8000`.

### Production checklist

1. **Database**: provision PostgreSQL, set in `.env`:
   ```env
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=hms
   POSTGRES_USER=hms
   POSTGRES_PASSWORD=<strong-password>
   POSTGRES_HOST=localhost
   ```
2. **Secrets**: generate a real `SECRET_KEY` (`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`), set `DEBUG=False`, restrict `ALLOWED_HOSTS` to the LAN IP/hostname.
3. **Serve**: run under Gunicorn (`gunicorn config.wsgi:application --bind 0.0.0.0:8000`) behind a Windows service or `nssm`; optionally nginx for static files.
4. **Static files**: `python manage.py collectstatic`.
5. **Backups**: schedule nightly `pg_dump` (or file copy for SQLite), retain ≥30 days, test restores.
6. **Windows firewall**: open only port 8000 (or 443 if TLS terminated at nginx).

## 5. Before pushing to GitHub

- [ ] `.env` is gitignored — **never commit real secrets** (verify with `git status` / `git ls-files | grep env`)
- [ ] `SECRET_KEY` in `.env` is a dev key only; production uses its own
- [ ] No patient data, dumps, or `db.sqlite3` in history (`git log --all --full-history -- db.sqlite3`)
- [ ] `.gitignore` covers `.venv/`, `__pycache__/`, `logs/`, `staticfiles/`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`
- [ ] `SECURITY.md` — define vulnerability reporting contact
- [ ] `LICENSE` — choose one (MIT/Apache-2.0/proprietary)
- [ ] README accurate and up to date (this file)
- [ ] CI optional: GitHub Actions running `uv sync && pytest && ruff check && mypy`
- [ ] If the repo is private vs public — decide deliberately; hospital software often stays private

## 6. How to run it

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv` or `pip install uv`)

### Setup

```bash
# clone / enter project
git clone <repo-url> HMS
cd HMS

# install dependencies (creates .venv from pyproject.toml)
uv sync

# configure environment
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/macOS
# edit .env if needed (defaults work out of the box)

# database
.venv\Scripts\python.exe manage.py migrate     # Windows
# .venv/bin/python manage.py migrate            # Linux/macOS

# admin user (first time)
.venv\Scripts\python.exe manage.py createsuperuser
```

### Run

```bash
.venv\Scripts\python.exe manage.py runserver 8000
```

Open <http://localhost:8000> → sign in → dashboard.

### Quality checks

```bash
.venv\Scripts\python.exe -m pytest     # tests
.venv\Scripts\ruff.exe check .         # lint
.venv\Scripts\python.exe -m mypy core patients config   # types
```

### Project layout

```
HMS/
├── config/          # Django project (settings, urls, db config)
├── core/            # User, roles (groups), audit log, permissions, middleware
├── patients/        # Patient registration & search
├── tests/           # pytest suite
├── templates/       # base + app templates (HTMX)
├── static/          # vendored htmx, css
├── logs/            # access/security/error/app rotating logs
├── .env             # local config (gitignored)
└── pyproject.toml   # deps + tool config
```

## Roadmap

- **Phase 2**: OPD encounters — check-in, queue, vitals, consult + ICD-10, 24h timers
- **Phase 3**: Orders & results — labs, pharmacy, MAR
- **Phase 4**: Billing — tariffs, invoices, payments
- **Phase 5**: Inpatient — wards, beds, admissions
- **Phase 6**: Reports & print templates
- **Phase 7**: Backups, Postgres migration, hardening
