from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import CommandError
import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with admin role'

    def add_arguments(self, parser):
        parser.add_argument('--email', help='Email for the superuser')
        parser.add_argument('--username', help='Username for the superuser')
        parser.add_argument('--first_name', help='First name for the superuser')
        parser.add_argument('--last_name', help='Last name for the superuser')

    def handle(self, *args, **options):
        email = options.get('email')
        username = options.get('username')
        first_name = options.get('first_name')
        last_name = options.get('last_name')

        # Get email if not provided
        if not email:
            email = input('Email: ')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email "{email}" already exists.')

        # Get username if not provided
        if not username:
            username = input('Username: ')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username "{username}" already exists.')

        # Get first name if not provided
        if not first_name:
            first_name = input('First name: ')

        # Get last name if not provided
        if not last_name:
            last_name = input('Last name: ')

        # Get password
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Password (again): ')

        if password != password_confirm:
            raise CommandError('Passwords do not match.')

        # Create superuser with admin role
        user = User.objects.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=User.ADMIN,  # Set role to admin
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_email_verified=True  # Auto-verify superuser email
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Superuser "{username}" ({email}) created successfully with admin role!'
            )
        )