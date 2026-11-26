import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    """Staff member. Roles are assigned via Django groups (see Role proxy)."""

    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    active_session_key = models.CharField(max_length=40, blank=True)
    must_change_password = models.BooleanField(default=False)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.primary_role_name})"

    @property
    def role_names(self):
        return sorted(g.name for g in self.groups.all())

    @property
    def primary_role_name(self):
        group = self.groups.order_by("name").first()
        return group.name if group else "No role"

    @property
    def role_group_names(self):
        return {g.name.lower() for g in self.groups.all()}


class Role(Group):
    """A 'role' is a named group of staff.

    Model-level permissions: Role.permissions (standard Django auth).
    Object-level permissions: assigned via django-guardian on this group,
    e.g. a Nurse role may only view encounters in her ward.
    """

    class Meta:
        proxy = True
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class AuditLog(models.Model):
    """Immutable record of who did what, when. Never updated or deleted."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    action = models.CharField(max_length=20)  # CREATE, UPDATE, DELETE, VIEW, LOGIN...
    model = models.CharField(max_length=100)
    object_id = models.CharField(max_length=64, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["model", "object_id"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.user} {self.action} {self.object_repr}"
