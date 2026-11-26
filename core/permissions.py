"""Authorization helpers.

Three layers, matching the permission model:
1. Role-based  -> user.role (broad: what kind of staff member)
2. Group-based -> Django groups + guardian permissions (what they can do)
3. Object-based -> guardian per-object permissions (which specific records)
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404

from .models import Role

# Roles allowed to see everything (subject to object perms).
PRIVILEGED_ROLES = {Role.ADMIN, Role.DOCTOR}


def role_required(*roles):
    """View decorator: user must be logged in and hold one of `roles`."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles and request.user.role != Role.ADMIN:
                raise PermissionDenied('Your role does not allow this action.')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def any_role_required(*roles):
    """Same as role_required but admin is not implicitly allowed."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied('Your role does not allow this action.')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def has_object_perm(user, obj, perm):
    """Object-level check via django-guardian.

    Superusers/admins and the object's assigned users bypass checks.
    Extend `perm` strings per model, e.g. 'patients.view_patient'.
    """
    if user.is_superuser or user.role == Role.ADMIN:
        return True
    return user.has_perm(perm, obj)


def get_object_or_404_with_perm(user, queryset, perm, **kwargs):
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(queryset, **kwargs)
    if not has_object_perm(user, obj, perm):
        raise Http404  # 404 not 403: don't leak existence of the record
    return obj
