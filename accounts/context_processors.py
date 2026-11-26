from django.conf import settings

from .models import PasswordResetRequest


def hms_context(request):
    """Globals expected by the hms-auth-ui templates."""
    pending = 0
    if request.user.is_authenticated:
        try:
            pending = PasswordResetRequest.objects.filter(
                status='pending').count()
        except Exception:
            pending = 0
    return {
        'HOSPITAL_NAME': getattr(settings, 'HOSPITAL_NAME',
                                 'Hospital Management System'),
        'APP_VERSION': getattr(settings, 'APP_VERSION', '1.0'),
        'HELP_DESK_LOCATION': getattr(settings, 'HELP_DESK_LOCATION',
                                      'the IT office'),
        'pending_reset_count': pending,
    }
