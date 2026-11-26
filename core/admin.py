from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'staff_id',
                    'department', 'is_active')
    list_filter = ('role', 'is_active', 'department')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Hospital profile', {'fields': ('role', 'staff_id', 'department', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Hospital profile', {'fields': ('role', 'staff_id', 'department', 'phone')}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'model', 'object_repr')
    list_filter = ('action', 'model')
    search_fields = ('user__username', 'object_repr')
    readonly_fields = ('id', 'user', 'action', 'model', 'object_id',
                       'object_repr', 'changes', 'ip_address', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
