import uuid

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class ICD10Code(models.Model):
    """Diagnoses reference table. Seeded with common codes; extend via admin."""

    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ["code"]
        verbose_name = "ICD-10 code"
        verbose_name_plural = "ICD-10 codes"

    def __str__(self):
        return f"{self.code} — {self.description}"


class Encounter(models.Model):
    """One patient visit. Everything clinical/financial hangs off this.

    State machine (see services.py):
      CHECKED_IN -> VITALS -> QUEUED -> WITH_DOCTOR -> CONSULTED
        -> DISPOSITION: DISCHARGED | ADMITTED | DETAINED -> (24h) -> DISCHARGED
    """

    class Type(models.TextChoices):
        OPD = "OPD", "Outpatient (OPD)"
        IPD = "IPD", "Inpatient (IPD)"
        EMERGENCY = "EMER", "Emergency"

    class Status(models.TextChoices):
        CHECKED_IN = "CHECKED_IN", "Checked in"
        VITALS = "VITALS", "Vitals recorded"
        QUEUED = "QUEUED", "In queue"
        WITH_DOCTOR = "WITH_DOCTOR", "With doctor"
        CONSULTED = "CONSULTED", "Consulted"
        DETAINED = "DETAINED", "Detained (observation)"
        ADMITTED = "ADMITTED", "Admitted"
        DISCHARGED = "DISCHARGED", "Discharged"
        CANCELLED = "CANCELLED", "Cancelled"

    OPEN_STATUSES = [
        Status.CHECKED_IN,
        Status.VITALS,
        Status.QUEUED,
        Status.WITH_DOCTOR,
        Status.CONSULTED,
        Status.DETAINED,
        Status.ADMITTED,
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.PROTECT, related_name="encounters"
    )
    encounter_type = models.CharField(
        max_length=4, choices=Type.choices, default=Type.OPD
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.CHECKED_IN
    )

    # Assignment
    service = models.CharField(max_length=100, blank=True)  # clinic/department
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="opd_encounters",
    )

    # Queue
    queue_number = models.PositiveIntegerField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=[("ROUTINE", "Routine"), ("URGENT", "Urgent"), ("EMERGENCY", "Emergency")],
        default="ROUTINE",
    )

    # Timestamps — diagnosis_at starts the 24h clock
    checked_in_at = models.DateTimeField(default=timezone.now)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="checked_in_encounters",
    )
    vitals_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    consultation_started_at = models.DateTimeField(null=True, blank=True)
    diagnosis_at = models.DateTimeField(null=True, blank=True)
    disposition = models.CharField(max_length=20, blank=True)  # DISCHARGED/ADMITTED/DETAINED
    discharged_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)

    chief_complaint = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-checked_in_at"]
        indexes = [
            models.Index(fields=["status", "checked_in_at"]),
            models.Index(fields=["patient", "-checked_in_at"]),
            models.Index(fields=["doctor", "status"]),
        ]

    def __str__(self):
        return f"{self.patient.mrn} · {self.get_encounter_type_display()} · {self.get_status_display()}"

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    @property
    def queue_token(self):
        if self.queue_number is None:
            return "—"
        prefix = {"OPD": "O", "IPD": "I", "EMER": "E"}.get(self.encounter_type, "X")
        return f"{prefix}{self.queue_number:03d}"

    @property
    def hours_since_diagnosis(self):
        if not self.diagnosis_at:
            return None
        return (timezone.now() - self.diagnosis_at).total_seconds() / 3600

    @property
    def is_24h_overdue(self):
        """Post-consult encounters older than 24h since diagnosis."""
        h = self.hours_since_diagnosis
        return h is not None and h >= 24 and self.is_open

    @classmethod
    def next_queue_number(cls, encounter_type, day=None):
        """Daily sequence per encounter type, allocated under a lock."""
        day = day or timezone.localdate()
        start = timezone.make_aware(
            timezone.datetime.combine(day, timezone.datetime.min.time())
        )
        end = start + timezone.timedelta(days=1)
        with transaction.atomic():
            last = (
                cls.objects.select_for_update()
                .filter(checked_in_at__gte=start, checked_in_at__lt=end,
                        encounter_type=encounter_type, queue_number__isnull=False)
                .order_by("-queue_number")
                .values_list("queue_number", flat=True)
                .first()
            )
            return (last or 0) + 1


class Vitals(models.Model):
    """Nurse-recorded vitals for an encounter. One row per recording."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="vitals"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="recorded_vitals",
    )
    recorded_at = models.DateTimeField(default=timezone.now)

    bp_systolic = models.PositiveSmallIntegerField(null=True, blank=True)
    bp_diastolic = models.PositiveSmallIntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    pulse = models.PositiveSmallIntegerField(null=True, blank=True)
    spo2 = models.PositiveSmallIntegerField(null=True, blank=True)
    respiratory_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"Vitals {self.encounter.queue_token} @ {self.recorded_at:%H:%M}"

    @property
    def bmi(self):
        if self.weight_kg and self.height_cm:
            h = float(self.height_cm) / 100
            return round(float(self.weight_kg) / (h * h), 1)
        return None

    @property
    def has_abnormal(self):
        checks = [
            self.bp_systolic and (self.bp_systolic >= 140 or self.bp_systolic < 90),
            self.bp_diastolic and (self.bp_diastolic >= 90 or self.bp_diastolic < 60),
            self.temperature and (float(self.temperature) >= 38.0 or float(self.temperature) < 36.0),
            self.pulse and (self.pulse >= 100 or self.pulse < 50),
            self.spo2 and self.spo2 < 94,
            self.respiratory_rate and (self.respiratory_rate >= 24 or self.respiratory_rate < 12),
        ]
        return any(checks)


class ClinicalNote(models.Model):
    """Immutable clinical note — consult (SOAP), nurse, or progress.

    Corrections create new notes; rows are never edited after creation.
    """

    class Type(models.TextChoices):
        CONSULT = "CONSULT", "Doctor consultation (SOAP)"
        NURSE = "NURSE", "Nursing note"
        PROGRESS = "PROGRESS", "Progress note"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(
        Encounter, on_delete=models.PROTECT, related_name="notes"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="clinical_notes",
    )
    note_type = models.CharField(max_length=10, choices=Type.choices)
    subjective = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    assessment = models.TextField(blank=True)
    plan = models.TextField(blank=True)
    diagnoses = models.ManyToManyField(ICD10Code, blank=True, related_name="notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_note_type_display()} — {self.encounter} @ {self.created_at:%Y-%m-%d %H:%M}"
