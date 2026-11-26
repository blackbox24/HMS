from django.contrib import admin

from .models import ClinicalNote, Encounter, ICD10Code, Vitals


class VitalsInline(admin.TabularInline):
    model = Vitals
    extra = 0
    readonly_fields = [f.name for f in Vitals._meta.fields]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class NoteInline(admin.TabularInline):
    model = ClinicalNote
    extra = 0
    readonly_fields = [f.name for f in ClinicalNote._meta.fields]
    can_delete = False
    fields = ['note_type', 'author', 'created_at', 'assessment']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ['queue_token', 'patient', 'encounter_type', 'status',
                    'doctor', 'checked_in_at', 'diagnosis_at']
    list_filter = ['status', 'encounter_type', 'priority']
    search_fields = ['patient__mrn', 'patient__first_name',
                     'patient__last_name']
    readonly_fields = ['checked_in_at', 'diagnosis_at', 'discharged_at',
                       'created_at', 'updated_at']
    inlines = [VitalsInline, NoteInline]


@admin.register(ICD10Code)
class ICD10CodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'description']
    search_fields = ['code', 'description']


@admin.register(Vitals)
class VitalsAdmin(admin.ModelAdmin):
    list_display = ['encounter', 'recorded_by', 'recorded_at', 'bp_systolic',
                    'temperature', 'pulse', 'spo2']


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ['encounter', 'note_type', 'author', 'created_at']
    readonly_fields = [f.name for f in ClinicalNote._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
