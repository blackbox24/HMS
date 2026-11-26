import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from core.audit import audit
from core.permissions import role_required
from patients.models import Patient

from . import services
from .models import Encounter, ICD10Code

logger = logging.getLogger(__name__)

OPD_ROLES = ("Receptionist", "Nurse", "Doctor")
STAFF_ROLES = OPD_ROLES + ("Lab Technician", "Pharmacist", "Billing Clerk")


def _is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


def _back(request, encounter):
    """HTMX actions redirect the whole page so all sections stay in sync."""
    url = f"/encounters/{encounter.pk}/"
    if _is_htmx(request):
        response = HttpResponse('')
        response['HX-Redirect'] = url
        return response
    return redirect(url)


def _get_encounter(pk):
    encounter = (Encounter.objects
                 .select_related('patient', 'doctor', 'checked_in_by')
                 .prefetch_related('vitals', 'notes__author', 'notes__diagnoses')
                 .filter(pk=pk).first())
    if encounter is None:
        raise Http404("Encounter not found")
    return encounter


# ------------------------------------------------------------- OPD board ----

@role_required(*OPD_ROLES)
def opd_board(request):
    today = timezone.localdate()
    start = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time()))
    encounters = (Encounter.objects
                  .filter(checked_in_at__gte=start,
                          status__in=Encounter.OPEN_STATUSES)
                  .select_related('patient', 'doctor')
                  .order_by('queue_number'))
    groups = {
        'queue': encounters.filter(status__in=[
            Encounter.Status.CHECKED_IN, Encounter.Status.VITALS,
            Encounter.Status.QUEUED]),
        'with_doctor': encounters.filter(status=Encounter.Status.WITH_DOCTOR),
        'consulted': encounters.filter(status=Encounter.Status.CONSULTED),
        'detained': encounters.filter(status=Encounter.Status.DETAINED),
        'admitted': encounters.filter(status=Encounter.Status.ADMITTED),
    }
    return render(request, 'encounters/opd_board.html', {
        'active_nav': 'opd',
        'groups': groups,
        'overdue_count': sum(1 for e in encounters if e.is_24h_overdue),
    })


# ------------------------------------------------------------- check-in -----

@role_required(*OPD_ROLES)
@require_http_methods(['GET', 'POST'])
def check_in(request):
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST.get('patient'))
        encounter = services.check_in(
            request,
            patient,
            encounter_type=request.POST.get('encounter_type', Encounter.Type.OPD),
            service=request.POST.get('service', '').strip(),
            priority=request.POST.get('priority', 'ROUTINE'),
            chief_complaint=request.POST.get('chief_complaint', '').strip(),
        )
        messages.success(
            request, f"{patient.full_name} checked in — token {encounter.queue_token}")
        return _back(request, encounter)

    q = request.GET.get('q', '').strip()
    patients = Patient.objects.none()
    if len(q) >= 2:
        patients = (Patient.objects
                    .filter(Q(mrn__icontains=q) | Q(first_name__icontains=q)
                            | Q(last_name__icontains=q) | Q(phone__icontains=q))
                    [:10])
    return render(request, 'encounters/check_in.html', {
        'active_nav': 'opd',
        'q': q,
        'patients': patients,
        'types': Encounter.Type.choices,
        'priorities': [
            ('ROUTINE', 'Routine'), ('URGENT', 'Urgent'),
            ('EMERGENCY', 'Emergency')],
    })


# ----------------------------------------------------------- encounter ------

@role_required(*STAFF_ROLES)
def encounter_detail(request, pk):
    encounter = _get_encounter(pk)
    audit(request, 'VIEW', encounter)
    doctors = _doctor_choices(request.user)
    return render(request, 'encounters/detail.html', {
        'active_nav': 'opd',
        'encounter': encounter,
        'doctors': doctors,
        'icd10': ICD10Code.objects.all()[:500],
        'can_consult': _can_consult(request.user, encounter),
        'can_nurse': _in_roles(request.user, ('Nurse', 'Doctor')),
    })


def _in_roles(user, roles):
    names = {g.name.lower() for g in user.groups.all()}
    return user.is_superuser or bool(names & {r.lower() for r in roles}) \
        or 'administrator' in names


def _doctor_choices(user):
    user_model = get_user_model()
    doctors = user_model.objects.filter(groups__name__iexact='Doctor')
    doctors |= user_model.objects.filter(is_superuser=True)
    return doctors.distinct().order_by('first_name', 'last_name')


def _can_consult(user, encounter):
    if encounter.doctor_id and encounter.doctor_id != user.pk \
            and not user.is_superuser and 'administrator' not in {
                g.name.lower() for g in user.groups.all()}:
        return False
    return _in_roles(user, ('Doctor',))


# ------------------------------------------------------------- actions ------

@role_required(*OPD_ROLES)
@require_http_methods(['POST'])
def record_vitals(request, pk):
    encounter = _get_encounter(pk)
    data = {f: request.POST.get(f) for f in (
        'bp_systolic', 'bp_diastolic', 'temperature', 'pulse', 'spo2',
        'respiratory_rate', 'weight_kg', 'height_cm')}
    data = {k: (v if v not in ('', None) else None) for k, v in data.items()}
    try:
        services.record_vitals(request, encounter, **data)
        messages.success(request, 'Vitals recorded.')
    except ValueError as e:
        messages.error(request, str(e))
    return _back(request, encounter)


@role_required(*OPD_ROLES)
@require_http_methods(['POST'])
def queue_action(request, pk):
    encounter = _get_encounter(pk)
    action = request.POST.get('action')
    try:
        if action == 'queue':
            services.send_to_queue(request, encounter)
        elif action == 'assign':
            doctor = get_object_or_404(
                get_user_model(), pk=request.POST.get('doctor'))
            services.assign_doctor(request, encounter, doctor)
        elif action == 'cancel':
            services.cancel(request, encounter,
                            request.POST.get('reason', ''))
        else:
            raise ValueError('Unknown action')
        messages.success(request, f'Encounter updated: {encounter.get_status_display()}.')
    except (ValueError, Http404) as e:
        messages.error(request, str(e))
    return _back(request, encounter)


@role_required('Doctor')
@require_http_methods(['POST'])
def consult(request, pk):
    encounter = _get_encounter(pk)
    if encounter.doctor_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied('Only the assigned doctor can consult.')
    try:
        services.save_consult(
            request, encounter,
            subjective=request.POST.get('subjective', '').strip(),
            objective=request.POST.get('objective', '').strip(),
            assessment=request.POST.get('assessment', '').strip(),
            plan=request.POST.get('plan', '').strip(),
            icd10_ids=request.POST.getlist('icd10'),
        )
        messages.success(request, 'Consultation saved — 24h clock started.')
    except ValueError as e:
        messages.error(request, str(e))
    return _back(request, encounter)


@role_required('Doctor')
@require_http_methods(['POST'])
def dispose(request, pk):
    encounter = _get_encounter(pk)
    try:
        services.dispose(request, encounter,
                         request.POST.get('disposition', ''))
        messages.success(request, 'Disposition recorded.')
    except ValueError as e:
        messages.error(request, str(e))
    return _back(request, encounter)


@role_required('Nurse', 'Doctor')
@require_http_methods(['POST'])
def add_note(request, pk):
    encounter = _get_encounter(pk)
    text = request.POST.get('note', '').strip()
    if text:
        try:
            services.add_note(request, encounter, text)
            messages.success(request, 'Note added.')
        except ValueError as e:
            messages.error(request, str(e))
    return _back(request, encounter)
