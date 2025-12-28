from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from getpass import getpass
import sys

User = get_user_model()

class Command(BaseCommand):
    help = 'Create or update admin user for EduTrack system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Admin email address',
            default='admin@edutrack.com'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='Admin first name',
            default='Admin'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Admin last name',
            default='User'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Admin password (if not provided, will prompt)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing admin user'
        )

    def handle(self, *args, **options):
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        password = options['password']
        force = options['force']

        self.stdout.write(
            self.style.SUCCESS('🔐 EduTrack Admin User Creation')
        )
        self.stdout.write('=' * 40)

        # Check if user exists
        try:
            admin_user = User.objects.get(email=email)
            if not force:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Admin user {email} already exists!')
                )
                confirm = input('Do you want to update it? (y/N): ')
                if confirm.lower() != 'y':
                    self.stdout.write('❌ Operation cancelled.')
                    return
            
            self.stdout.write(f'📝 Updating existing admin user: {email}')
            created = False
        except User.DoesNotExist:
            self.stdout.write(f'➕ Creating new admin user: {email}')
            admin_user = User(email=email, username=email)
            created = True

        # Get password if not provided
        if not password:
            while True:
                password = getpass('Enter password (min 8 characters): ')
                if len(password) >= 8:
                    confirm_password = getpass('Confirm password: ')
                    if password == confirm_password:
                        break
                    else:
                        self.stdout.write(
                            self.style.ERROR('❌ Passwords don\'t match. Try again.')
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Password must be at least 8 characters long.')
                    )

        try:
            # Set user details
            admin_user.first_name = first_name
            admin_user.last_name = last_name
            admin_user.role = 'teacher'  # Use teacher role for admin
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.set_password(password)
            admin_user.save()

            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user {"created" if created else "updated"} successfully!')
            )
            self.stdout.write(f'📧 Email: {admin_user.email}')
            self.stdout.write(f'👤 Name: {admin_user.get_full_name()}')
            self.stdout.write(f'🔑 Password: [Hidden for security]')
            self.stdout.write(f'🌐 Admin URL: http://localhost:8000/admin/')
            
            # Show quick test
            self.stdout.write('\n🧪 Quick Test:')
            self.stdout.write('1. Start server: python manage.py runserver')
            self.stdout.write('2. Visit: http://localhost:8000/admin/')
            self.stdout.write(f'3. Login with: {admin_user.email}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {e}')
            )
            sys.exit(1)