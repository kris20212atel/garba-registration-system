from django.contrib import admin
from .models import Child, DailyAttendance, DailyGift, EventConfig


@admin.register(EventConfig)
class EventConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_day', 'total_days', 'start_date', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['registration_id', 'name', 'guardian_name', 'phone', 'age', 'gender', 'created_at']
    list_filter = ['gender']
    search_fields = ['registration_id', 'name', 'guardian_name', 'phone']
    readonly_fields = ['registration_id', 'created_at', 'updated_at']
    ordering = ['registration_id']


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ['child', 'event_day', 'entry_time', 'created_at']
    list_filter = ['event_day']
    search_fields = ['child__registration_id', 'child__name']
    ordering = ['event_day', 'entry_time']
    readonly_fields = ['created_at']


@admin.register(DailyGift)
class DailyGiftAdmin(admin.ModelAdmin):
    list_display = ['child', 'event_day', 'gift_time', 'status', 'operator', 'created_at']
    list_filter = ['event_day', 'status']
    search_fields = ['child__registration_id', 'child__name']
    ordering = ['event_day', 'gift_time']
    readonly_fields = ['created_at']
