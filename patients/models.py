import uuid

from django.db import models, transaction
from django.utils import timezone


class Patient(models.Model):
    """Master patient index. MRN is assigned once and never changes."""

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class BloodGroup(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"
        UNKNOWN = "U", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mrn = models.CharField(max_length=20, unique=True, editable=False)

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    previous_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    blood_group = models.CharField(
        max_length=3, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN
    )

    phone = models.CharField(max_length=20, blank=True)
    alt_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    nhis_number = models.CharField(max_length=30, blank=True, db_index=True)
    nhis_expiry = models.DateField(null=True, blank=True)

    # Next of kin
    nok_name = models.CharField(max_length=200, blank=True)
    nok_relationship = models.CharField(max_length=50, blank=True)
    nok_phone = models.CharField(max_length=20, blank=True)

    # National ID / passport for unique identification
    national_id = models.CharField(max_length=30, blank=True)

    is_deceased = models.BooleanField(default=False)
    deceased_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    registered_by = models.ForeignKey(
        "core.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="registered_patients",
    )
    registered_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [models.Index(fields=["last_name", "first_name"]), models.Index(fields=["phone"])]

    def __str__(self):
        return f"{self.full_name} ({self.mrn})"

    def save(self, *args, **kwargs):
        if not self.mrn:
            self.mrn = self.generate_mrn()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)

    @property
    def age(self):
        today = timezone.localdate()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

    @classmethod
    def generate_mrn(cls):
        """Format: HMS-YYYY-NNNNNN e.g. HMS-2026-000123"""
        year = timezone.now().year
        prefix = f"HMS-{year}-"
        with transaction.atomic():
            last = (
                cls.objects.select_for_update()
                .filter(mrn__startswith=prefix)
                .order_by("-mrn")
                .values_list("mrn", flat=True)
                .first()
            )
            seq = int(last.rsplit("-", 1)[1]) + 1 if last else 1
            return f"{prefix}{seq:06d}"
