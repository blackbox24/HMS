"""Flag encounters that have passed the 24h post-diagnosis window.

OPD patients awaiting disposition and detained (observation) patients must
be discharged or admitted within 24h of the doctor's diagnosis. This command
logs each overdue encounter and writes an audit entry; run it from Task
Scheduler / cron every hour. It does NOT auto-discharge — disposition is a
clinical decision.
"""
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.audit import AuditLog
from encounters.models import Encounter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Report encounters past the 24h post-diagnosis window."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        overdue = (Encounter.objects
                   .filter(status__in=Encounter.OPEN_STATUSES,
                           diagnosis_at__lt=cutoff)
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
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{count} encounter(s) past the 24h window."))
