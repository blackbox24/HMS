from .models import AuditLog


def audit(request, action, instance, changes=None):
    """Write an audit entry for a model instance.

    Usage: audit(request, 'CREATE', patient) or
           audit(request, 'UPDATE', patient, changes={'phone': [old, new]})
    """
    return AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model=instance._meta.label,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        changes=changes or {},
        ip_address=_client_ip(request),
    )


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
