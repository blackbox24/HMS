from django.db import migrations

DEFAULT_ROLES = [
    "Administrator",
    "Receptionist",
    "Nurse",
    "Doctor",
    "Lab Technician",
    "Pharmacist",
    "Billing Clerk",
]


def seed_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in DEFAULT_ROLES:
        Group.objects.get_or_create(name=name)


def unseed_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=DEFAULT_ROLES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_role_remove_user_role"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
