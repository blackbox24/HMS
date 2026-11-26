from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from patients.models import Patient

from .models import AuditLog


@login_required
def dashboard(request):
    from encounters.models import Encounter
    from accounts.models import PasswordResetRequest

    groups = request.user.role_group_names
    is_admin = request.user.is_superuser or "administrator" in groups
    is_doctor = is_admin or "doctor" in groups
    is_nurse = is_admin or "nurse" in groups
    is_receptionist = is_admin or "receptionist" in groups
    today = timezone.localdate()

    open_encounters = Encounter.objects.filter(status__in=Encounter.OPEN_STATUSES)
    today_encounters = Encounter.objects.filter(queue_date=today)

    role = "Staff"
    if is_admin:
        role = "Administrator"
    elif is_doctor:
        role = "Doctor"
    elif is_nurse:
        role = "Nurse"
    elif is_receptionist:
        role = "Receptionist"
    elif "lab technician" in groups:
        role = "Lab technician"
    elif "pharmacist" in groups:
        role = "Pharmacist"
    elif "billing clerk" in groups:
        role = "Billing clerk"

    assigned_encounters = Encounter.objects.none()
    if is_doctor:
        assigned_encounters = open_encounters.filter(doctor=request.user).select_related(
            "patient"
        ).order_by("assigned_at", "checked_in_at")[:8]

    waiting_vitals = open_encounters.filter(
        status__in=[Encounter.Status.CHECKED_IN, Encounter.Status.VITALS]
    ).select_related("patient").order_by("checked_in_at")[:8]

    work_queue = open_encounters.select_related("patient", "doctor").order_by(
        "-priority", "checked_in_at"
    )[:8]

    ctx = {
        "active_nav": "dashboard",
        "dashboard_role": role,
        "total_patients": Patient.objects.count(),
        "open_encounters": open_encounters.count(),
        "today_check_ins": today_encounters.count(),
        "waiting_count": open_encounters.filter(
            status__in=[
                Encounter.Status.CHECKED_IN,
                Encounter.Status.VITALS,
                Encounter.Status.QUEUED,
            ]
        ).count(),
        "doctor_queue_count": open_encounters.filter(
            status__in=[Encounter.Status.QUEUED, Encounter.Status.WITH_DOCTOR]
        ).count(),
        "assigned_encounters": assigned_encounters,
        "waiting_vitals": waiting_vitals,
        "work_queue": work_queue,
        "recent_patients": Patient.objects.order_by("-registered_at")[:5],
        "recent_activity": AuditLog.objects.select_related("user")[:10],
        "staff_count": get_user_model().objects.filter(is_active=True).count(),
        "pending_reset_count": PasswordResetRequest.objects.filter(
            status=PasswordResetRequest.Status.PENDING
        ).count(),
    }
    return render(request, "core/dashboard.html", ctx)
