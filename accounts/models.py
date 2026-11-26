from django.conf import settings
from django.db import models


class PasswordResetRequest(models.Model):
    """LAN-friendly password reset: staff request a reset, an admin
    issues a one-time temporary password and hands it over in person.
    The plain temp password is never stored."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ISSUED = 'issued', 'Issued'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='password_reset_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.PENDING)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                  on_delete=models.SET_NULL,
                                  related_name='issued_reset_requests')
    issued_at = models.DateTimeField(null=True, blank=True)
    handed_over_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('issue_temp_password', 'Can issue temporary passwords'),
        ]

    def __str__(self):
        return f'{self.user.username} — {self.get_status_display()} ({self.created_at:%Y-%m-%d %H:%M})'

    @property
    def reference(self):
        return f'PR-{self.pk:04d}'
