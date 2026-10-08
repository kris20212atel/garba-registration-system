"""
Management command to seed demo data for the Navratri EMS.
Run: python manage.py seed_demo
"""
import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.base import ContentFile
from events.models import Child, DailyAttendance, DailyGift, EventConfig


def _make_placeholder_photo(name):
    """Generate a minimal valid PNG as placeholder photo."""
    # Minimal 1x1 PNG (orange pixel)
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x8f'
        b'\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return ContentFile(png_bytes, name=f'{name}.png')


DEMO_CHILDREN = [
    {'name': 'Rahul Patel',    'guardian_name': 'Amit Patel',    'phone': '9876543210', 'age': 8,  'gender': 'M', 'notes': 'Allergic to nuts'},
    {'name': 'Riya Patel',     'guardian_name': 'Amit Patel',    'phone': '9876543210', 'age': 6,  'gender': 'F', 'notes': ''},
    {'name': 'Aarav Patel',    'guardian_name': 'Amit Patel',    'phone': '9876543210', 'age': 10, 'gender': 'M', 'notes': ''},
    {'name': 'Priya Sharma',   'guardian_name': 'Suresh Sharma', 'phone': '9123456780', 'age': 7,  'gender': 'F', 'notes': ''},
    {'name': 'Arjun Mehta',    'guardian_name': 'Deepak Mehta',  'phone': '9988776655', 'age': 9,  'gender': 'M', 'notes': ''},
    {'name': 'Kavya Joshi',    'guardian_name': 'Rohit Joshi',   'phone': '9112233445', 'age': 5,  'gender': 'F', 'notes': ''},
    {'name': 'Dev Gupta',      'guardian_name': 'Sanjay Gupta',  'phone': '9667788990', 'age': 11, 'gender': 'M', 'notes': ''},
    {'name': 'Ananya Singh',   'guardian_name': 'Vikram Singh',  'phone': '9556677881', 'age': 8,  'gender': 'F', 'notes': ''},
    {'name': 'Rohan Verma',    'guardian_name': 'Prakash Verma', 'phone': '9445566772', 'age': 12, 'gender': 'M', 'notes': ''},
    {'name': 'Ishaan Kumar',   'guardian_name': 'Vijay Kumar',   'phone': '9334455663', 'age': 7,  'gender': 'M', 'notes': ''},
]


class Command(BaseCommand):
    help = 'Seed demo data for the Navratri EMS'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            DailyGift.objects.all().delete()
            DailyAttendance.objects.all().delete()
            Child.objects.all().delete()
            self.stdout.write(self.style.WARNING('Data cleared.'))

        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@navratri.local', 'navratri2026')
            self.stdout.write(self.style.SUCCESS('[OK] Admin user created: admin / navratri2026'))
        else:
            self.stdout.write('[SKIP] Admin user already exists.')

        # Event config
        config = EventConfig.get_config()
        config.name = 'Navratri 2026'
        config.total_days = 20
        config.current_day = 4
        config.save()
        self.stdout.write(self.style.SUCCESS(f'[OK] Event config: Day {config.current_day}/{config.total_days}'))

        # Create children
        now = timezone.now()
        created_children = []
        base_time = now.replace(hour=19, minute=30, second=0, microsecond=0)

        for i, data in enumerate(DEMO_CHILDREN):
            if Child.objects.filter(name=data['name'], phone=data['phone']).exists():
                child = Child.objects.get(name=data['name'], phone=data['phone'])
                self.stdout.write(f'  [SKIP] {child.registration_id} - {child.name}')
            else:
                child = Child(**data)
                child.save()
                child.photo.save(
                    f'{child.registration_id}.png',
                    _make_placeholder_photo(child.registration_id),
                    save=True
                )
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created {child.registration_id} - {child.name}'))
            created_children.append(child)

        # Seed daily attendance & gifts for Days 1, 2, 3
        self.stdout.write('\nSeeding daily records...')

        for day in range(1, 4):
            for j, child in enumerate(created_children[:7]):
                entry_time = base_time - timedelta(days=(4 - day)) + timedelta(minutes=j * 5)

                att, created = DailyAttendance.objects.get_or_create(
                    child=child, event_day=day,
                    defaults={'entry_time': entry_time}
                )
                if created:
                    self.stdout.write(f'  [OK] Day {day} Entry: {child.registration_id}')

                if not (day == 2 and j == 6):
                    gift_time = entry_time + timedelta(minutes=8)
                    gift, created = DailyGift.objects.get_or_create(
                        child=child, event_day=day,
                        defaults={'gift_time': gift_time, 'status': 'GIVEN'}
                    )
                    if created:
                        self.stdout.write(f'  [OK] Day {day} Gift:  {child.registration_id}')

        total = Child.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'\nDemo data seeded! Total children: {total}\n'
            f'Admin: admin / navratri2026\n'
            f'Current day: {config.current_day}\n'
            f'NAV001/NAV002/NAV003 share phone 9876543210\n'
        ))
