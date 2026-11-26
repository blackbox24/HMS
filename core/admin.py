import contextlib

from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from guardian.admin import GuardedModelAdminMixin

from .models import AuditLog, PasswordResetRequest, Role, User

# Replace the default flat Group admin — roles ARE groups (same table).
with contextlib.suppress(NotRegistered):
    admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "roles_display",
        "staff_id",
        "department",
        "is_active",
    )
    list_filter = ("is_active", "department", "groups")
    search_fields = ("username", "first_name", "last_name", "email", "staff_id")
    fieldsets = BaseUserAdmin.fieldsets + (  # type: ignore[operator]
        ("Hospital profile", {"fields": ("staff_id", "department", "phone")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Hospital profile", {"fields": ("staff_id", "department", "phone")}),
    )
    filter_horizontal = ("groups",)

    @admin.display(description="Roles")
    def roles_display(self, obj):
        return ", ".join(obj.role_names) or "—"


@admin.register(Role)
class RoleAdmin(GuardedModelAdminMixin, GroupAdmin):  # type: ignore[misc]
    """Roles = groups. Assign model perms via 'Permissions' and per-object
    perms via the guardian 'Object permissions' section."""


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "requested_at", "status", "handled_by", "handled_at")
    list_filter = ("status",)
    readonly_fields = ("requested_at", "handled_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "model", "object_repr")
    list_filter = ("action", "model")
    search_fields = ("user__username", "object_repr")
    readonly_fields = (
        "id",
        "user",
        "action",
        "model",
        "object_id",
        "object_repr",
        "changes",
        "ip_address",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
