from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from patients.models import Patient

from .models import AuditLog


@login_required
def dashboard(request):
    ctx = {
        "total_patients": Patient.objects.count(),
        "recent_patients": Patient.objects.order_by("-registered_at")[:5],
        "recent_activity": AuditLog.objects.select_related("user")[:10],
    }
    return render(request, "core/dashboard.html", ctx)
