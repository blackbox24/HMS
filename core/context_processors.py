"""Navigation context processor.

Builds the sidebar sections each request, showing only the modules the
logged-in user's roles/permissions actually allow — mirrors the
role_required decorators on the views.
"""
from django.urls import reverse

# Keep in sync with the view decorators:
#   encounters.views.OPD_ROLES / PATIENT_ROLES (patients.views)
OPD_ROLES = {"receptionist", "nurse", "doctor"}
PATIENT_ROLES = OPD_ROLES | {"billing clerk", "lab technician", "pharmacist"}


def _item(label, url_name, key, url_args=None):
    try:
        return {"label": label, "url": reverse(url_name, args=url_args or []),
                "key": key}
    except Exception:
        return None


def nav_sections(request):
    user = request.user
    if not user.is_authenticated:
        return {"nav_sections": []}

    groups = {g.name.lower() for g in user.groups.all()}
    is_admin = user.is_superuser or "administrator" in groups

    def can(*roles):
        return is_admin or bool(groups & set(roles))

    def section(title, items):
        items = [i for i in items if i]
        return {"title": title, "items": items} if items else None

    sections = [
        section("General", [
            _item("Dashboard", "dashboard", "dashboard"),
        ]),
        section("Clinical", [
            _item("OPD board", "opd_board", "opd") if can(*OPD_ROLES) else None,
            _item("Check-in patient", "check_in", "check_in")
            if can(*OPD_ROLES) else None,
        ]),
        section("Records", [
            _item("Patients", "patient_list", "patients")
            if can(*PATIENT_ROLES) else None,
            _item("Register patient", "patient_create", "patients")
            if can(*PATIENT_ROLES) else None,
        ]),
        section("Administration", [
            _item("Password resets", "accounts:password_resets",
                  "password_resets")
            if (user.is_superuser
                or user.has_perm("accounts.issue_temp_password")) else None,
            {"label": "Django admin", "url": "/admin/", "key": "django_admin"}
            if user.is_staff else None,
            {"label": "Change password",
             "url": reverse("accounts:password_change"), "key": "password_change"},
        ]),
    ]
    return {"nav_sections": [s for s in sections if s]}
