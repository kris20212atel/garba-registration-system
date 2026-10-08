"""
Tests for the Navratri Child Gift & Entry Management System.
Tests cover all 10 critical business rules.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from .models import Child, DailyAttendance, DailyGift, EventConfig


class ChildRegistrationTests(TestCase):
    """Tests for child registration rules."""

    def test_registration_id_is_unique(self):
        """Registration IDs are unique (cannot create two children with same ID)."""
        child1 = Child.objects.create(
            name='Rahul Patel', guardian_name='Amit', phone='9876543210'
        )
        # Try to create another child with same registration_id
        child2 = Child(
            registration_id=child1.registration_id,
            name='Riya Patel', guardian_name='Amit', phone='9876543210'
        )
        with self.assertRaises(IntegrityError):
            child2.save()

    def test_registration_ids_auto_generated_sequential(self):
        """Registration IDs are auto-generated as 1, 2, 3, etc."""
        child1 = Child.objects.create(name='Child One', guardian_name='G1', phone='9111111111')
        child2 = Child.objects.create(name='Child Two', guardian_name='G2', phone='9222222222')
        child3 = Child.objects.create(name='Child Three', guardian_name='G3', phone='9333333333')

        self.assertEqual(child1.registration_id, '1')
        self.assertEqual(child2.registration_id, '2')
        self.assertEqual(child3.registration_id, '3')

    def test_phone_numbers_are_not_unique(self):
        """Multiple children can share the same phone number."""
        phone = '9876543210'
        child1 = Child.objects.create(name='Child A', guardian_name='Guardian', phone=phone)
        child2 = Child.objects.create(name='Child B', guardian_name='Guardian', phone=phone)
        child3 = Child.objects.create(name='Child C', guardian_name='Guardian', phone=phone)

        # All three should be created successfully
        self.assertEqual(Child.objects.filter(phone=phone).count(), 3)
        # But they have different IDs
        ids = {child1.registration_id, child2.registration_id, child3.registration_id}
        self.assertEqual(len(ids), 3)

    def test_registration_id_format(self):
        """Registration ID must be a plain positive integer string."""
        child = Child.objects.create(name='Test Child', guardian_name='Guardian', phone='9111111111')
        self.assertTrue(child.registration_id.isdigit())
        self.assertGreater(int(child.registration_id), 0)


class DailyAttendanceTests(TestCase):
    """Tests for daily entry rules."""

    def setUp(self):
        self.child = Child.objects.create(
            name='Rahul Patel', guardian_name='Amit', phone='9876543210'
        )

    def test_child_can_enter_on_different_days(self):
        """A child can enter on different days."""
        DailyAttendance.objects.create(child=self.child, event_day=1)
        DailyAttendance.objects.create(child=self.child, event_day=2)
        DailyAttendance.objects.create(child=self.child, event_day=3)
        DailyAttendance.objects.create(child=self.child, event_day=20)

        self.assertEqual(DailyAttendance.objects.filter(child=self.child).count(), 4)

    def test_child_cannot_enter_twice_on_same_day(self):
        """A child cannot enter twice on the same day — DB constraint."""
        DailyAttendance.objects.create(child=self.child, event_day=5)
        with self.assertRaises(IntegrityError):
            DailyAttendance.objects.create(child=self.child, event_day=5)

    def test_previous_day_entry_does_not_block_today(self):
        """Entry on day 1 does not prevent entry on day 2."""
        DailyAttendance.objects.create(child=self.child, event_day=1)
        # Day 2 should work fine
        attendance = DailyAttendance.objects.create(child=self.child, event_day=2)
        self.assertEqual(attendance.event_day, 2)

    def test_entry_uniqueness_is_per_child_per_day(self):
        """Different children can enter on the same day."""
        child2 = Child.objects.create(name='Riya', guardian_name='Amit', phone='9876543210')
        DailyAttendance.objects.create(child=self.child, event_day=5)
        # Different child, same day — should work
        DailyAttendance.objects.create(child=child2, event_day=5)
        self.assertEqual(DailyAttendance.objects.filter(event_day=5).count(), 2)


class DailyGiftTests(TestCase):
    """Tests for daily gift distribution rules."""

    def setUp(self):
        self.child = Child.objects.create(
            name='Rahul Patel', guardian_name='Amit', phone='9876543210'
        )

    def test_child_can_receive_gift_on_different_days(self):
        """A child can receive gifts on different days."""
        DailyGift.objects.create(child=self.child, event_day=1, status='GIVEN')
        DailyGift.objects.create(child=self.child, event_day=2, status='GIVEN')
        DailyGift.objects.create(child=self.child, event_day=3, status='GIVEN')
        DailyGift.objects.create(child=self.child, event_day=20, status='GIVEN')

        self.assertEqual(DailyGift.objects.filter(child=self.child).count(), 4)

    def test_child_cannot_receive_two_gifts_on_same_day(self):
        """A child cannot receive two gifts on the same day — DB constraint."""
        DailyGift.objects.create(child=self.child, event_day=3, status='GIVEN')
        with self.assertRaises(IntegrityError):
            DailyGift.objects.create(child=self.child, event_day=3, status='GIVEN')

    def test_previous_day_gift_does_not_block_today(self):
        """Gift on day 1 does not prevent gift on day 2."""
        DailyGift.objects.create(child=self.child, event_day=1, status='GIVEN')
        # Day 2 must work
        gift = DailyGift.objects.create(child=self.child, event_day=2, status='GIVEN')
        self.assertEqual(gift.event_day, 2)
        self.assertEqual(gift.status, 'GIVEN')

    def test_gift_uniqueness_is_per_child_per_day(self):
        """Different children can receive gifts on the same day."""
        child2 = Child.objects.create(name='Riya', guardian_name='Amit', phone='9876543210')
        DailyGift.objects.create(child=self.child, event_day=5, status='GIVEN')
        # Different child, same day — should work
        DailyGift.objects.create(child=child2, event_day=5, status='GIVEN')
        self.assertEqual(DailyGift.objects.filter(event_day=5).count(), 2)

    def test_complete_20_day_scenario(self):
        """A child can receive one gift per day for all 20 days."""
        for day in range(1, 21):
            DailyGift.objects.create(child=self.child, event_day=day, status='GIVEN')

        self.assertEqual(DailyGift.objects.filter(child=self.child).count(), 20)


class ViewTests(TestCase):
    """Tests for views and authentication."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.config = EventConfig.get_config()
        self.config.current_day = 7
        self.config.save()
        self.child = Child.objects.create(
            name='Rahul Patel', guardian_name='Amit', phone='9876543210'
        )

    def test_dashboard_requires_login(self):
        """Dashboard must redirect unauthenticated users to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_authenticated_dashboard_loads(self):
        """Authenticated user can access dashboard."""
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_entry_page_loads(self):
        """Entry page loads for authenticated users."""
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('entry'))
        self.assertEqual(response.status_code, 200)

    def test_invalid_registration_id_returns_not_found(self):
        """Invalid registration ID returns not-found result."""
        self.client.login(username='admin', password='pass')
        response = self.client.post(reverse('entry'), {'registration_id': 'NAV999'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'REGISTRATION NOT FOUND')

    def test_valid_registration_id_returns_child(self):
        """Valid registration ID shows child details."""
        self.client.login(username='admin', password='pass')
        response = self.client.post(reverse('entry'), {'registration_id': self.child.registration_id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CHILD FOUND')
        self.assertContains(response, self.child.name)

    def test_record_entry_api(self):
        """Recording entry via API returns success."""
        self.client.login(username='admin', password='pass')
        response = self.client.post(
            reverse('record_entry', args=[self.child.pk]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_duplicate_entry_api_returns_409(self):
        """Duplicate entry returns 409 Conflict."""
        self.client.login(username='admin', password='pass')
        # First entry
        self.client.post(reverse('record_entry', args=[self.child.pk]), content_type='application/json')
        # Second entry — same day
        response = self.client.post(
            reverse('record_entry', args=[self.child.pk]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'DUPLICATE')

    def test_record_gift_api(self):
        """Recording gift via API returns success."""
        self.client.login(username='admin', password='pass')
        response = self.client.post(
            reverse('record_gift', args=[self.child.pk]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_duplicate_gift_api_returns_409(self):
        """Duplicate gift returns 409 Conflict."""
        self.client.login(username='admin', password='pass')
        # First gift
        self.client.post(reverse('record_gift', args=[self.child.pk]), content_type='application/json')
        # Second gift — same day
        response = self.client.post(
            reverse('record_gift', args=[self.child.pk]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'DUPLICATE')

    def test_search_by_phone_returns_multiple_children(self):
        """Searching by shared phone number returns all matching children."""
        phone = '9876543210'
        child2 = Child.objects.create(name='Riya Patel', guardian_name='Amit', phone=phone)
        child3 = Child.objects.create(name='Aarav Patel', guardian_name='Amit', phone=phone)

        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('search'), {'q': phone})
        self.assertEqual(response.status_code, 200)
        # All three children with this phone should appear
        self.assertContains(response, self.child.name)
        self.assertContains(response, child2.name)
        self.assertContains(response, child3.name)

    def test_complete_scenario_nav001(self):
        """
        Full scenario test for NAV001:
        Day 1: Entry allowed, Gift allowed
        Day 1 again: Entry rejected, Gift rejected
        Day 2: Entry allowed, Gift allowed
        Day 20: Entry allowed, Gift allowed
        """
        # Day 1
        self.config.current_day = 1
        self.config.save()

        self.client.login(username='admin', password='pass')

        # Day 1 - Entry allowed
        r = self.client.post(reverse('record_entry', args=[self.child.pk]), content_type='application/json')
        self.assertTrue(r.json()['success'])

        # Day 1 - Gift allowed
        r = self.client.post(reverse('record_gift', args=[self.child.pk]), content_type='application/json')
        self.assertTrue(r.json()['success'])

        # Day 1 again - Entry rejected
        r = self.client.post(reverse('record_entry', args=[self.child.pk]), content_type='application/json')
        self.assertFalse(r.json()['success'])
        self.assertEqual(r.status_code, 409)

        # Day 1 again - Gift rejected
        r = self.client.post(reverse('record_gift', args=[self.child.pk]), content_type='application/json')
        self.assertFalse(r.json()['success'])
        self.assertEqual(r.status_code, 409)

        # Day 2 - Entry allowed
        self.config.current_day = 2
        self.config.save()

        r = self.client.post(reverse('record_entry', args=[self.child.pk]), content_type='application/json')
        self.assertTrue(r.json()['success'])

        # Day 2 - Gift allowed
        r = self.client.post(reverse('record_gift', args=[self.child.pk]), content_type='application/json')
        self.assertTrue(r.json()['success'])

        # Day 20 - Entry and Gift allowed
        self.config.current_day = 20
        self.config.save()

        r = self.client.post(reverse('record_entry', args=[self.child.pk]), content_type='application/json')
        self.assertTrue(r.json()['success'])

        r = self.client.post(reverse('record_gift', args=[self.child.pk]), content_type='application/json')
        self.assertTrue(r.json()['success'])

        # Verify all 3 days recorded
        self.assertEqual(DailyAttendance.objects.filter(child=self.child).count(), 3)
        self.assertEqual(DailyGift.objects.filter(child=self.child).count(), 3)
