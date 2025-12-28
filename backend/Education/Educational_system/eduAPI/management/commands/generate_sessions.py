# backend/Education/Educational_system/eduAPI/management/commands/generate_sessions.py
# Django management command for generating sessions from templates

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from ...services.session_generator import SessionGeneratorService


class Command(BaseCommand):
    help = 'Generate live sessions from active templates'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Generate sessions for specific date (YYYY-MM-DD format)',
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=1,
            help='Number of days ahead to generate sessions for (default: 1)',
        )
        parser.add_argument(
            '--cleanup-logs',
            action='store_true',
            help='Clean up old generation logs',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without actually creating sessions',
        )
    
    def handle(self, *args, **options):
        generator = SessionGeneratorService()
        
        # Clean up old logs if requested
        if options['cleanup_logs']:
            self.stdout.write('Cleaning up old generation logs...')
            deleted_count = generator.cleanup_old_logs()
            self.stdout.write(
                self.style.SUCCESS(f'Cleaned up {deleted_count} old log entries')
            )
        
        # Determine target date(s)
        if options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
                target_dates = [target_date]
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                )
                return
        else:
            # Generate for today and upcoming days
            today = timezone.now().date()
            days_ahead = options['days_ahead']
            target_dates = [today + timedelta(days=i) for i in range(days_ahead)]
        
        # Dry run mode
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No sessions will be created')
            )
            self.show_dry_run_preview(target_dates)
            return
        
        # Generate sessions
        total_generated = 0
        total_failed = 0
        total_skipped = 0
        
        for target_date in target_dates:
            self.stdout.write(f'\nGenerating sessions for {target_date}...')
            
            try:
                result = generator.generate_sessions_for_date(target_date)
                
                total_generated += result['generated']
                total_failed += result['failed']
                total_skipped += result['skipped']
                
                if result['generated'] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Generated {result["generated"]} sessions'
                        )
                    )
                
                if result['failed'] > 0:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Failed to generate {result["failed"]} sessions'
                        )
                    )
                
                if result['skipped'] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  - Skipped {result["skipped"]} templates'
                        )
                    )
                
                if result['generated'] == 0 and result['failed'] == 0:
                    self.stdout.write('  No sessions needed for this date')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error processing {target_date}: {str(e)}')
                )
                total_failed += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('GENERATION SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(f'Total sessions generated: {total_generated}')
        self.stdout.write(f'Total failures: {total_failed}')
        self.stdout.write(f'Total skipped: {total_skipped}')
        
        if total_generated > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully generated {total_generated} sessions!')
            )
        
        if total_failed > 0:
            self.stdout.write(
                self.style.ERROR(f'\n✗ {total_failed} generation attempts failed')
            )
    
    def show_dry_run_preview(self, target_dates):
        """Show what would be generated without actually creating sessions"""
        from ...models.recurring_sessions_models import SessionTemplate
        
        for target_date in target_dates:
            self.stdout.write(f'\nPreview for {target_date}:')
            
            active_templates = SessionTemplate.objects.filter(
                status='ACTIVE',
                start_date__lte=target_date
            ).exclude(
                end_date__lt=target_date
            )
            
            if not active_templates.exists():
                self.stdout.write('  No active templates found')
                continue
            
            for template in active_templates:
                # Check if this template would generate a session
                day_matches = target_date.weekday() == template.day_of_week
                has_assignments = template.group_assignments.filter(is_active=True).exists()
                
                if day_matches and has_assignments:
                    assigned_students = sum(
                        assignment.group.students.count() 
                        for assignment in template.group_assignments.filter(is_active=True)
                    )
                    
                    self.stdout.write(
                        f'  ✓ Would generate: "{template.title}" '
                        f'({assigned_students} students)'
                    )
                else:
                    reason = []
                    if not day_matches:
                        reason.append('wrong day')
                    if not has_assignments:
                        reason.append('no assignments')
                    
                    self.stdout.write(
                        f'  - Would skip: "{template.title}" ({", ".join(reason)})'
                    )