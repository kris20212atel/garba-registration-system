from django import forms
from django.core.exceptions import ValidationError
from .models import Child, EventConfig
import os


ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


class ChildRegistrationForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'guardian_name', 'phone', 'photo', 'age', 'gender', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Full name of child'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Parent or guardian name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '10-digit phone number', 'type': 'tel'}),
            'photo': forms.FileInput(attrs={'class': 'form-control form-control-lg', 'accept': 'image/*'}),
            'age': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Age (optional)', 'min': 1, 'max': 18}),
            'gender': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes (optional)'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'content_type'):
            if photo.content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError('Only JPEG, PNG, WebP, or GIF images are allowed.')
            if photo.size > MAX_IMAGE_SIZE:
                raise ValidationError('Image must be under 5 MB.')
        return photo

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits.')
        if len(phone) < 10 or len(phone) > 15:
            raise ValidationError('Phone number must be between 10 and 15 digits.')
        return phone


class ChildEditForm(forms.ModelForm):
    """Edit form - photo is optional (keep existing if not changed)."""
    class Meta:
        model = Child
        fields = ['name', 'guardian_name', 'phone', 'photo', 'age', 'gender', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'type': 'tel'}),
            'photo': forms.FileInput(attrs={'class': 'form-control form-control-lg', 'accept': 'image/*'}),
            'age': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'min': 1, 'max': 18}),
            'gender': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Photo is not required on edit
        self.fields['photo'].required = False

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'content_type'):
            if photo.content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError('Only JPEG, PNG, WebP, or GIF images are allowed.')
            if photo.size > MAX_IMAGE_SIZE:
                raise ValidationError('Image must be under 5 MB.')
        return photo

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits.')
        if len(phone) < 10 or len(phone) > 15:
            raise ValidationError('Phone number must be between 10 and 15 digits.')
        return phone


class EventConfigForm(forms.ModelForm):
    class Meta:
        model = EventConfig
        fields = ['name', 'start_date', 'total_days', 'current_day']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30}),
            'current_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total_days = cleaned_data.get('total_days')
        current_day = cleaned_data.get('current_day')
        if total_days and current_day:
            if current_day > total_days:
                raise ValidationError('Current day cannot exceed total days.')
            if current_day < 1:
                raise ValidationError('Current day must be at least 1.')
        return cleaned_data


class QuickDayForm(forms.Form):
    """For quickly changing the current event day from the navbar."""
    current_day = forms.IntegerField(min_value=1, max_value=20)
