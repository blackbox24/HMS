import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'
    NURSE = 'NURSE', 'Nurse'
    DOCTOR = 'DOCTOR', 'Doctor'
    LAB_TECH = 'LAB_TECH', 'Lab Technician'
    PHARMACIST = 'PHARMACIST', 'Pharmacist'
    BILLING = 'BILLING', 'Billing Clerk'


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.ADMIN)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECEPTIONIST)
    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    active_session_key = models.CharField(max_length=40, blank=True)

    objects = UserManager()

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def role_group_names(self):
        return {g.name for g in self.groups.all()}


class AuditLog(models.Model):
    """Immutable record of who did what, when. Never updated or deleted."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name='audit_logs')
    action = models.CharField(max_length=20)  # CREATE, UPDATE, DELETE, VIEW, LOGIN...
    model = models.CharField(max_length=100)
    object_id = models.CharField(max_length=64, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['model', 'object_id']),
                   models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f'{self.created_at:%Y-%m-%d %H:%M} {self.user} {self.action} {self.object_repr}'
