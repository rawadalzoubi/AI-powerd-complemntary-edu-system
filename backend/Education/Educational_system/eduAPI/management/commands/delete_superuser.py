from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import CommandError

User = get_user_model()

class Command(BaseCommand):
    help = 'Delete superuser accounts'

    def add_arguments(self, parser):
        parser.add_argument('--email', help='Email of the superuser to delete')
        parser.add_argument('--username', help='Username of the superuser to delete')
        parser.add_argument('--list', action='store_true', help='List all superusers')
        parser.add_argument('--all', action='store_true', help='Delete ALL superusers (dangerous!)')

    def handle(self, *args, **options):
        if options['list']:
            self.list_superusers()
            return

        if options['all']:
            self.delete_all_superusers()
            return

        email = options.get('email')
        username = options.get('username')

        if not email and not username:
            raise CommandError('Please provide either --email or --username or use --list to see all superusers')

        if email:
            self.delete_by_email(email)
        elif username:
            self.delete_by_username(username)

    def list_superusers(self):
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(self.style.WARNING('No superusers found.'))
            return

        self.stdout.write(self.style.SUCCESS('Current Superusers:'))
        self.stdout.write('=' * 50)
        
        for user in superusers:
            self.stdout.write(
                f"ID: {user.id} | Username: {user.username} | Email: {user.email} | Role: {user.role}"
            )

    def delete_by_email(self, email):
        try:
            user = User.objects.get(email=email, is_superuser=True)
            username = user.username
            user.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" ({email}) deleted successfully!')
            )
        except User.DoesNotExist:
            raise CommandError(f'Superuser with email "{email}" not found.')

    def delete_by_username(self, username):
        try:
            user = User.objects.get(username=username, is_superuser=True)
            email = user.email
            user.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" ({email}) deleted successfully!')
            )
        except User.DoesNotExist:
            raise CommandError(f'Superuser with username "{username}" not found.')

    def delete_all_superusers(self):
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(self.style.WARNING('No superusers found to delete.'))
            return

        # Show warning
        self.stdout.write(
            self.style.WARNING('⚠️  WARNING: This will delete ALL superuser accounts!')
        )
        
        for user in superusers:
            self.stdout.write(f"- {user.username} ({user.email})")
        
        confirm = input('\nAre you sure? Type "DELETE ALL" to confirm: ')
        
        if confirm == "DELETE ALL":
            count = superusers.count()
            superusers.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {count} superuser account(s)!')
            )
        else:
            self.stdout.write(self.style.ERROR('❌ Operation cancelled.'))