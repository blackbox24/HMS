from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('mrn', 'full_name', 'date_of_birth', 'gender', 'phone', 'nhis_number')
    list_filter = ('gender', 'blood_group')
    search_fields = ('mrn', 'first_name', 'last_name', 'phone', 'nhis_number',
                     'national_id')
    readonly_fields = ('mrn', 'registered_by', 'registered_at', 'updated_at')
