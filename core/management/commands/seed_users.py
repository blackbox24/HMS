"""Seed roles (groups), their model permissions, and one demo user per role.

Idempotent — safe to run multiple times. Permissions use standard Django
codenames. Per-record (object-level) permissions are assigned later via the
admin's guardian "Object permissions" section on each role.

Usage:
    python manage.py seed_users                       # default password
    python manage.py seed_users --password 'Secret123'
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

User = get_user_model()

DEFAULT_PASSWORD = 'Hms@2026!'

# role name -> (is_staff, model perms [(app_label, model, codename)...] or 'ALL')
ROLE_DEFS = {
    'Administrator': {
        'staff': True,
        'perms': 'ALL',
    },
    'Receptionist': {
        'staff': False,
        'perms': [
            ('patients', 'patient', 'add_patient'),
            ('patients', 'patient', 'view_patient'),
            ('patients', 'patient', 'change_patient'),
            ('encounters', 'encounter', 'add_encounter'),
            ('encounters', 'encounter', 'view_encounter'),
            ('encounters', 'encounter', 'change_encounter'),
            ('encounters', 'clinicalnote', 'view_clinicalnote'),
        ],
    },
    'Nurse': {
        'staff': False,
        'perms': [
            ('patients', 'patient', 'view_patient'),
            ('encounters', 'encounter', 'view_encounter'),
            ('encounters', 'encounter', 'change_encounter'),
            ('encounters', 'vitals', 'add_vitals'),
            ('encounters', 'vitals', 'view_vitals'),
            ('encounters', 'clinicalnote', 'add_clinicalnote'),
            ('encounters', 'clinicalnote', 'view_clinicalnote'),
        ],
    },
    'Doctor': {
        'staff': False,
        'perms': [
            ('patients', 'patient', 'view_patient'),
            ('patients', 'patient', 'change_patient'),
            ('encounters', 'encounter', 'view_encounter'),
            ('encounters', 'encounter', 'change_encounter'),
            ('encounters', 'vitals', 'view_vitals'),
            ('encounters', 'clinicalnote', 'add_clinicalnote'),
            ('encounters', 'clinicalnote', 'view_clinicalnote'),
            ('encounters', 'icd10code', 'view_icd10code'),
        ],
    },
    'Lab Technician': {
        'staff': False,
        'perms': [
            ('patients', 'patient', 'view_patient'),
        ],
    },
    'Pharmacist': {
        'staff': False,
        'perms': [
            ('patients', 'patient', 'view_patient'),
        ],
    },
    'Billing Clerk': {
        'staff': False,
        'perms': [
            ('patients', 'patient', 'view_patient'),
            ('patients', 'patient', 'change_patient'),
        ],
    },
}

# role name -> demo username
DEMO_USERS = {
    'Administrator': 'admin',
    'Receptionist': 'receptionist',
    'Nurse': 'nurse',
    'Doctor': 'doctor',
    'Lab Technician': 'labtech',
    'Pharmacist': 'pharmacist',
    'Billing Clerk': 'billing',
}


def _perm_lookup(app_label, model, codename):
    return Permission.objects.get(
        content_type__app_label=app_label,
        content_type__model=model,
        codename=codename,
    )


class Command(BaseCommand):
    help = 'Create roles, assign permissions, and create demo users per role.'

    def add_arguments(self, parser):
        parser.add_argument('--password', default=DEFAULT_PASSWORD,
                            help='Password for demo users (default: %(default)s)')

    def handle(self, *args, **options):
        password = options['password']
        if len(password) < 8:
            raise CommandError('Password must be at least 8 characters.')

        for role_name, cfg in ROLE_DEFS.items():
            group, _ = Group.objects.get_or_create(name=role_name)
            self._assign_model_perms(group, cfg['perms'])
            self._ensure_user(DEMO_USERS[role_name], role_name, cfg['staff'],
                              password)
            self.stdout.write(self.style.SUCCESS(f'  role "{role_name}" ready'))

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete. Demo password: {password} '
            '(change it after first login)'))

    def _assign_model_perms(self, group, spec):
        if spec == 'ALL':
            group.permissions.set(Permission.objects.all())
            return
        perms = []
        for app_label, model, codename in spec:
            try:
                perms.append(_perm_lookup(app_label, model, codename))
            except Permission.DoesNotExist:
                self.stderr.write(self.style.WARNING(
                    f'    ! permission {app_label}.{model}.{codename} '
                    'not found, skipped'))
        group.permissions.add(*perms)

    def _ensure_user(self, username, role_name, is_staff, password):
        group = Group.objects.get(name=role_name)
        user = User.objects.filter(Q(username__iexact=username)).first()
        if user is None:
            user = User(username=username,
                        email=f'{username}@hms.local',
                        is_staff=is_staff)
            user.set_password(password)
            user.save()
            created = True
        else:
            created = False

        user.groups.add(group)
        if is_staff and not user.is_staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])

        verb = 'created' if created else 'exists'
        self.stdout.write(f'    user "{username}" ({role_name}) {verb}')
