from django.contrib import admin

from .models import PasswordResetRequest


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status', 'issued_by', 'issued_at',
                    'handed_over_at')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'issued_at', 'handed_over_at')
