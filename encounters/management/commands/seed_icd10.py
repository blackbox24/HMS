"""Seed a starter set of common ICD-10 codes.

Extend via /admin/encounters/icd10code/ or add rows here and re-run —
existing codes are never overwritten.
"""
from django.core.management.base import BaseCommand

from encounters.models import ICD10Code

CODES = [
    ("A09", "Gastroenteritis and colitis of presumed infectious origin"),
    ("B54", "Malaria, unspecified"),
    ("D50.9", "Iron deficiency anaemia, unspecified"),
    ("E10.9", "Type 1 diabetes mellitus without complications"),
    ("E11.9", "Type 2 diabetes mellitus without complications"),
    ("E78.5", "Hyperlipidaemia, unspecified"),
    ("G43.9", "Migraine, unspecified"),
    ("G44.2", "Tension-type headache"),
    ("H10.9", "Conjunctivitis, unspecified"),
    ("I10", "Essential (primary) hypertension"),
    ("I25.9", "Chronic ischaemic heart disease, unspecified"),
    ("J00", "Acute nasopharyngitis (common cold)"),
    ("J02.9", "Acute pharyngitis, unspecified"),
    ("J06.9", "Acute upper respiratory infection, unspecified"),
    ("J11.1", "Influenza with other respiratory manifestations"),
    ("J18.9", "Pneumonia, unspecified organism"),
    ("J45.9", "Asthma, unspecified"),
    ("K02.9", "Dental caries, unspecified"),
    ("K08.8", "Other specified disorders of teeth and supporting structures"),
    ("K29.7", "Gastritis, unspecified"),
    ("K35.8", "Acute appendicitis, other and unspecified"),
    ("K52.9", "Noninfective gastroenteritis and colitis, unspecified"),
    ("L02.9", "Cutaneous abscess, furuncle and carbuncle, unspecified"),
    ("L30.9", "Dermatitis, unspecified"),
    ("M25.5", "Pain in joint"),
    ("M54.5", "Low back pain"),
    ("M79.1", "Myalgia"),
    ("N18.9", "Chronic kidney disease, unspecified"),
    ("N39.0", "Urinary tract infection, site not specified"),
    ("O80", "Encounter for full-term uncomplicated delivery"),
    ("R05", "Cough"),
    ("R07.4", "Chest pain, unspecified"),
    ("R10.4", "Other and unspecified abdominal pain"),
    ("R11", "Nausea and vomiting"),
    ("R50.9", "Fever, unspecified"),
    ("R51", "Headache"),
    ("R52", "Pain, unspecified"),
    ("R56.9", "Convulsions, unspecified"),
    ("S72.9", "Fracture of femur, unspecified part"),
    ("S82.9", "Fracture of lower leg, unspecified part"),
    ("T14.0", "Concussion, unspecified part of body"),
    ("Z00.0", "General adult medical examination without abnormal findings"),
    ("Z34.9", "Supervision of normal pregnancy, unspecified"),
    ("Z76.9", "Persons encountering health services in unspecified circumstances"),
]


class Command(BaseCommand):
    help = "Seed common ICD-10 diagnosis codes (idempotent)."

    def handle(self, *args, **options):
        created = 0
        for code, desc in CODES:
            _, was_created = ICD10Code.objects.get_or_create(
                code=code, defaults={'description': desc})
            created += was_created
        self.stdout.write(self.style.SUCCESS(
            f"ICD-10 codes: {created} created, {len(CODES) - created} already present."))
