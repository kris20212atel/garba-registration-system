import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import EventConfig

class Command(BaseCommand):
    help = 'Automatically initialize database with EventConfig and default admin if missing'

    def handle(self, *args, **options):
        # 1. Initialize EventConfig
        config = EventConfig.get_config()
        self.stdout.write(self.style.SUCCESS(f'[OK] EventConfig verified: Day {config.current_day}/{config.total_days}'))

        # 2. Initialize default admin user if no superuser exists
        admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@navratri.local')

        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Superuser created: {admin_username} / {admin_password}'))
        else:
            self.stdout.write(f'[OK] Superuser {admin_username} already exists.')
