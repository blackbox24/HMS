"""Encounter state machine — all transitions go through here.

Keeps business rules out of views: status changes, timestamps, queue
number allocation, audit logging, and the 24h diagnosis clock.
"""
import logging

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.audit import audit

from .models import ClinicalNote, Encounter, Vitals

logger = logging.getLogger(__name__)

# status -> statuses it may move to (disposition handled separately)
TRANSITIONS = {
    Encounter.Status.CHECKED_IN: {Encounter.Status.VITALS, Encounter.Status.QUEUED,
                                  Encounter.Status.CANCELLED},
    Encounter.Status.VITALS: {Encounter.Status.QUEUED, Encounter.Status.WITH_DOCTOR,
                              Encounter.Status.CANCELLED},
    Encounter.Status.QUEUED: {Encounter.Status.WITH_DOCTOR, Encounter.Status.CANCELLED},
    Encounter.Status.WITH_DOCTOR: {Encounter.Status.CONSULTED, Encounter.Status.QUEUED,
                                   Encounter.Status.CANCELLED},
    Encounter.Status.CONSULTED: {Encounter.Status.DETAINED, Encounter.Status.ADMITTED,
                                 Encounter.Status.DISCHARGED, Encounter.Status.QUEUED},
    Encounter.Status.DETAINED: {Encounter.Status.ADMITTED, Encounter.Status.DISCHARGED,
                                Encounter.Status.CANCELLED},
    Encounter.Status.ADMITTED: {Encounter.Status.DISCHARGED},
}


def _transition(request, encounter, new_status, **fields):
    allowed = TRANSITIONS.get(encounter.status, set())
    if new_status not in allowed:
        raise ValueError(
            f"Cannot move encounter from {encounter.status} to {new_status}")
    old = encounter.status
    encounter.status = new_status
    for k, v in fields.items():
        setattr(encounter, k, v)
    encounter.save()
    audit(request, "UPDATE", encounter,
          changes={"status": f"{old} -> {new_status}"})
    logger.info("Encounter %s: %s -> %s by %s",
                encounter.pk, old, new_status, request.user)
    return encounter


@transaction.atomic
def check_in(request, patient, encounter_type=Encounter.Type.OPD,
             service="", priority="ROUTINE", chief_complaint=""):
    """Register arrival: creates the encounter and issues a queue number.

    Retries on unique-constraint collision so concurrent check-ins can't
    duplicate a daily token even if the sequence read raced.
    """
    queue_date = timezone.localdate()
    encounter = None
    for _ in range(3):
        try:
            with transaction.atomic():
                queue_number = Encounter.next_queue_number(
                    encounter_type, day=queue_date)
                encounter = Encounter.objects.create(
                    patient=patient,
                    encounter_type=encounter_type,
                    service=service,
                    priority=priority,
                    chief_complaint=chief_complaint,
                    queue_number=queue_number,
                    queue_date=queue_date,
                    checked_in_by=request.user,
                )
            break
        except IntegrityError:
            continue
    if encounter is None:
        raise IntegrityError("Could not allocate a queue number, try again")
    audit(request, "CREATE", encounter,
          changes={"check_in": patient.mrn,
                   "queue_token": encounter.queue_token})
    logger.info("Checked in %s as %s by %s",
                patient.mrn, encounter.queue_token, request.user)
    return encounter


@transaction.atomic
def record_vitals(request, encounter, **data):
    """Save vitals; first recording moves CHECKED_IN -> VITALS."""
    vitals = Vitals.objects.create(
        encounter=encounter, recorded_by=request.user, **data)
    if encounter.status == Encounter.Status.CHECKED_IN:
        _transition(request, encounter, Encounter.Status.VITALS,
                    vitals_at=timezone.now())
    audit(request, "CREATE", vitals,
          changes={"encounter": str(encounter.pk)})
    return vitals


@transaction.atomic
def send_to_queue(request, encounter):
    """Vitals done (or skipped) — patient waits for a doctor."""
    return _transition(request, encounter, Encounter.Status.QUEUED)


@transaction.atomic
def assign_doctor(request, encounter, doctor):
    """Assign/reassign a consultant.

    From QUEUED/VITALS/CHECKED_IN this pulls the patient out of the queue
    (-> WITH_DOCTOR). From WITH_DOCTOR it just swaps the consultant —
    e.g. the assigned doctor was called away.
    """
    encounter.doctor = doctor
    encounter.assigned_at = timezone.now()
    encounter.save()
    if encounter.status == Encounter.Status.WITH_DOCTOR:
        audit(request, "UPDATE", encounter,
              changes={"doctor": f"reassigned -> {doctor}"})
        return encounter
    return _transition(request, encounter, Encounter.Status.WITH_DOCTOR)


@transaction.atomic
def save_consult(request, encounter, subjective="", objective="",
                 assessment="", plan="", icd10_ids=None):
    """Doctor's SOAP note. First consult stamps diagnosis_at — starts 24h."""
    if encounter.status != Encounter.Status.WITH_DOCTOR:
        raise ValueError("Encounter is not with a doctor")

    note = ClinicalNote.objects.create(
        encounter=encounter, author=request.user,
        note_type=ClinicalNote.Type.CONSULT,
        subjective=subjective, objective=objective,
        assessment=assessment, plan=plan,
    )
    if icd10_ids:
        note.diagnoses.set(icd10_ids)

    fields = {}
    if encounter.consultation_started_at is None:
        fields["consultation_started_at"] = timezone.now()
    if encounter.diagnosis_at is None:
        fields["diagnosis_at"] = timezone.now()  # 24h clock starts here
    _transition(request, encounter, Encounter.Status.CONSULTED, **fields)
    audit(request, "CREATE", note, changes={"consult": str(encounter.pk)})
    return note


@transaction.atomic
def add_note(request, encounter, text,
            note_type=ClinicalNote.Type.NURSE):
    """Nurse/progress note — allowed on any open encounter."""
    if not encounter.is_open:
        raise ValueError("Encounter is closed")
    note = ClinicalNote.objects.create(
        encounter=encounter, author=request.user, note_type=note_type,
        assessment=text,
    )
    audit(request, "CREATE", note, changes={"note": str(encounter.pk)})
    return note


@transaction.atomic
def dispose(request, encounter, disposition):
    """Post-consult disposition: DISCHARGED | ADMITTED | DETAINED."""
    mapping = {
        "DISCHARGED": Encounter.Status.DISCHARGED,
        "ADMITTED": Encounter.Status.ADMITTED,
        "DETAINED": Encounter.Status.DETAINED,
    }
    if disposition not in mapping:
        raise ValueError(f"Unknown disposition: {disposition}")
    fields = {"disposition": disposition}
    if disposition == "DISCHARGED":
        fields["discharged_at"] = timezone.now()
    return _transition(request, encounter, mapping[disposition], **fields)


@transaction.atomic
def cancel(request, encounter, reason=""):
    return _transition(request, encounter, Encounter.Status.CANCELLED,
                       cancel_reason=reason)
