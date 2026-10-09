from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class EventConfig(models.Model):
    """Stores global event configuration - only one record should exist."""
    name = models.CharField(max_length=200, default='Navratri 2026')
    start_date = models.DateField(null=True, blank=True)
    total_days = models.IntegerField(default=20)
    current_day = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Event Configuration'

    def __str__(self):
        return f"{self.name} - Day {self.current_day}/{self.total_days}"

    @classmethod
    def get_config(cls):
        config, created = cls.objects.get_or_create(pk=1, defaults={
            'name': 'Navratri 2026',
            'total_days': 20,
            'current_day': 1,
        })
        return config


def child_photo_upload_path(instance, filename):
    """Upload child photos to media/photos/child_id/filename"""
    ext = filename.rsplit('.', 1)[-1].lower()
    return f'photos/{instance.registration_id}.{ext}'


class Child(models.Model):
    """Represents a registered child."""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    registration_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    name = models.CharField(max_length=200)
    guardian_name = models.CharField(max_length=200)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10,15}$', 'Enter a valid phone number (10-15 digits).')]
    )
    photo = models.ImageField(upload_to=child_photo_upload_path, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Child'
        verbose_name_plural = 'Children'

    def __str__(self):
        return f"{self.registration_id} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = self._generate_registration_id()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_registration_id():
        """Generate next available sequential ID in format 2026-1, 2026-2, etc."""
        prefix = '2026-'
        all_ids = Child.objects.values_list('registration_id', flat=True)
        max_num = 0
        for rid in all_ids:
            if rid:
                val = str(rid).strip()
                if val.startswith(prefix):
                    val = val[len(prefix):]
                try:
                    num = int(val)
                    if num > max_num:
                        max_num = num
                except (ValueError, TypeError):
                    pass
        return f"{prefix}{max_num + 1}"

    def get_history(self):
        """Return 20-day history for this child."""
        attendances = {a.event_day: a for a in self.dailyattendance_set.all()}
        gifts = {g.event_day: g for g in self.dailygift_set.all()}
        history = []
        for day in range(1, 21):
            history.append({
                'day': day,
                'attendance': attendances.get(day),
                'gift': gifts.get(day),
            })
        return history


class DailyAttendance(models.Model):
    """Records a child's daily entry. Unique per child per day."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    event_day = models.IntegerField()
    entry_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('child', 'event_day')]
        verbose_name = 'Daily Attendance'
        verbose_name_plural = 'Daily Attendances'
        ordering = ['event_day', 'entry_time']
        # DB-level unique constraint
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'event_day'],
                name='unique_child_day_attendance'
            )
        ]

    def __str__(self):
        return f"{self.child.registration_id} - Day {self.event_day} - {self.entry_time}"


class DailyGift(models.Model):
    """Records a child's daily gift. Unique per child per day."""
    STATUS_CHOICES = [
        ('GIVEN', 'Given'),
        ('PENDING', 'Pending'),
    ]

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    event_day = models.IntegerField()
    gift_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='GIVEN')
    operator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='gifts_given'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('child', 'event_day')]
        verbose_name = 'Daily Gift'
        verbose_name_plural = 'Daily Gifts'
        ordering = ['event_day', 'gift_time']
        # DB-level unique constraint
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'event_day'],
                name='unique_child_day_gift'
            )
        ]

    def __str__(self):
        return f"{self.child.registration_id} - Day {self.event_day} - {self.status}"
