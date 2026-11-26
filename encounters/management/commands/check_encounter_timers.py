"""Flag encounters that have passed the 24h post-diagnosis window.

OPD patients awaiting disposition (CONSULTED) and detained observation
patients (DETAINED) must be discharged or admitted within 24h of the
doctor's diagnosis. ADMITTED inpatients are excluded — their disposition
is already decided and stays open for days.

Each encounter is alerted once (overdue_alerted_at); run hourly from
Task Scheduler / cron. It does NOT auto-discharge — disposition is a
clinical decision.
"""
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.audit import AuditLog
from encounters.models import Encounter

logger = logging.getLogger(__name__)

WATCH_STATUSES = [Encounter.Status.CONSULTED, Encounter.Status.DETAINED]


class Command(BaseCommand):
    help = "Report encounters past the 24h post-diagnosis window."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        overdue = (Encounter.objects
                   .filter(status__in=WATCH_STATUSES,
                           diagnosis_at__lt=cutoff,
                           overdue_alerted_at__isnull=True)
                   .select_related('patient'))

        count = 0
        for e in overdue:
            hours = e.hours_since_diagnosis or 0
            logger.warning(
                "24h overdue: %s (%s) — diagnosed %.1fh ago, status %s",
                e.queue_token, e.patient.mrn, hours, e.status)
            AuditLog.objects.create(
                user=None, action='UPDATE', model=e._meta.label,
                object_id=str(e.pk), object_repr=str(e)[:255],
                changes={'timer': f'overdue {hours:.0f}h since diagnosis'})
            e.overdue_alerted_at = timezone.now()
            e.save(update_fields=['overdue_alerted_at'])
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{count} encounter(s) newly past the 24h window."))
