# backend/Education/Educational_system/eduAPI/management/commands/run_scheduler.py
# Management command to run the automatic session generator scheduler

import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from ...services.session_generator import SessionGeneratorService

logger = logging.getLogger(__name__)


def generate_sessions_job():
    """
    Job function to generate sessions from active templates
    """
    logger.info("Starting automatic session generation...")
    generator = SessionGeneratorService()
    
    try:
        result = generator.generate_sessions_for_date()
        logger.info(f"Session generation completed: {result}")
        
        if result['generated'] > 0:
            logger.info(f"✓ Generated {result['generated']} sessions")
        if result['failed'] > 0:
            logger.warning(f"✗ Failed to generate {result['failed']} sessions")
        if result['skipped'] > 0:
            logger.info(f"- Skipped {result['skipped']} templates")
            
    except Exception as e:
        logger.error(f"Error in session generation job: {str(e)}")


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    Delete old job execution records (older than 7 days by default)
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler for automatic session generation"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Run session generation every minute
        scheduler.add_job(
            generate_sessions_job,
            trigger=CronTrigger(minute="*"),  # Every minute for testing
            id="generate_sessions_job",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(
            self.style.SUCCESS("Added job 'generate_sessions_job' - runs every minute")
        )

        # Clean up old job executions daily
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(
            self.style.SUCCESS("Added job 'delete_old_job_executions' - runs daily at midnight")
        )

        try:
            self.stdout.write(self.style.SUCCESS("Starting scheduler..."))
            self.stdout.write(self.style.WARNING("Press Ctrl+C to exit"))
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Stopping scheduler..."))
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS("Scheduler shut down successfully!"))
