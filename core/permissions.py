"""Authorization helpers.

Three layers:
1. Role-based   -> group membership (a Role is a Django group; see core.Role)
2. Group perms  -> Django model permissions assigned to the role
3. Object perms -> django-guardian per-object permissions on the role
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404

ADMIN_GROUP = "Administrator"


def _group_names(user):
    return {g.name.lower() for g in user.groups.all()}


def is_admin(user):
    return user.is_superuser or ADMIN_GROUP.lower() in _group_names(user)


def role_required(*roles):
    """View decorator: user must be logged in and be in one of `roles`.

    Role names are matched case-insensitively. Superusers and members of the
    'Administrator' role always pass.
    """
    wanted = {r.lower() for r in roles}

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not (is_admin(request.user) or _group_names(request.user) & wanted):
                raise PermissionDenied("Your role does not allow this action.")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def any_role_required(*roles):
    """Same as role_required but admins are not implicitly allowed."""
    wanted = {r.lower() for r in roles}

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not (_group_names(request.user) & wanted):
                raise PermissionDenied("Your role does not allow this action.")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def has_object_perm(user, obj, perm):
    """Object-level check via django-guardian.

    Superusers/Administrator bypass; otherwise the user's roles' object
    permissions are evaluated by guardian's ObjectPermissionBackend.
    """
    if is_admin(user):
        return True
    return user.has_perm(perm, obj)


def get_object_or_404_with_perm(user, queryset, perm, **kwargs):
    from django.shortcuts import get_object_or_404

    obj = get_object_or_404(queryset, **kwargs)
    if not has_object_perm(user, obj, perm):
        raise Http404  # 404 not 403: don't leak existence of the record
    return obj
