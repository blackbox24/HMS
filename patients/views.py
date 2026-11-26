import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from core.audit import audit
from core.permissions import role_required

from .models import Patient

logger = logging.getLogger(__name__)

PAGE_SIZE = 25

PATIENT_ROLES = ("Receptionist", "Nurse", "Doctor", "Billing Clerk", "Lab Technician", "Pharmacist")


@role_required(*PATIENT_ROLES)
def patient_list(request):
    q = request.GET.get("q", "").strip()
    patients = Patient.objects.all()
    if q:
        patients = patients.filter(
            Q(mrn__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(phone__icontains=q)
            | Q(nhis_number__icontains=q)
            | Q(national_id__icontains=q)
        )

    page = Paginator(patients, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(
        request,
        "patients/list.html",
        {
            "page": page,
            "patients": page.object_list,
            "q": q,
        },
    )


@role_required(*PATIENT_ROLES)
@require_http_methods(["GET", "POST"])
def patient_create(request):
    if request.method == "POST":
        patient = Patient(
            first_name=request.POST.get("first_name", "").strip(),
            middle_name=request.POST.get("middle_name", "").strip(),
            last_name=request.POST.get("last_name", "").strip(),
            previous_name=request.POST.get("previous_name", "").strip(),
            date_of_birth=request.POST.get("date_of_birth"),
            gender=request.POST.get("gender"),
            phone=request.POST.get("phone", "").strip(),
            alt_phone=request.POST.get("alt_phone", "").strip(),
            email=request.POST.get("email", "").strip(),
            address=request.POST.get("address", "").strip(),
            nhis_number=request.POST.get("nhis_number", "").strip(),
            national_id=request.POST.get("national_id", "").strip(),
            nok_name=request.POST.get("nok_name", "").strip(),
            nok_relationship=request.POST.get("nok_relationship", "").strip(),
            nok_phone=request.POST.get("nok_phone", "").strip(),
            blood_group=request.POST.get("blood_group", "U"),
            notes=request.POST.get("notes", "").strip(),
            registered_by=request.user,
        )
        if not (
            patient.first_name and patient.last_name and patient.date_of_birth and patient.gender
        ):
            messages.error(request, "First name, last name, DOB and gender are required.")
            return redirect("patient_create")
        patient.save()
        audit(request, "CREATE", patient)
        logger.info("Patient registered: %s by %s", patient.mrn, request.user)
        messages.success(request, f"Patient registered: {patient.mrn}")
        return redirect("patient_detail", pk=patient.pk)

    return render(
        request,
        "patients/form.html",
        {
            "patient_blood_groups": Patient.BloodGroup.choices,
        },
    )


@role_required(*PATIENT_ROLES)
def patient_detail(request, pk):
    patient = Patient.objects.filter(pk=pk).first()
    if patient is None:
        raise Http404("Patient not found")
    audit(request, "VIEW", patient)
    return render(request, "patients/detail.html", {"patient": patient})
