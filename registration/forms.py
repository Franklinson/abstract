import uuid
import json
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Register
import os

def load_gand_data():
    file_path = settings.BASE_DIR / 'gand_data.json'  # Ensure this is the correct path
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if isinstance(data, dict) and "good_standing" in data and "not_in_good_standing" in data:
                return data
            else:
                raise ValueError("GAND data should contain 'good_standing' and 'not_in_good_standing' keys.")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading GAND data: {e}")  # Log the error for debugging
        return {"good_standing": [], "not_in_good_standing": []}  # Return a default structure
    except FileNotFoundError:
        print("GAND data file not found.")  # Log the error
        return {"good_standing": [], "not_in_good_standing": []}


def validate_gand_number(gand_number, name):
    gand_data = load_gand_data()
    
    for entry in gand_data.get("good_standing", []):
        if entry.get('GAND_number') == gand_number and entry.get('name') == name:
            return True
    for entry in gand_data.get("not_in_good_standing", []):
        if entry.get('GAND_number') == gand_number and entry.get('name') == name:
            return True
    return False


class RegisterForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = [
            'title', 'name', 'email', 'address', 'phone', 'gender', 'category',
            'gand_number', 'prof_of_status', 'profession', 'organization', 'about_us', 'complaince'
        ]

    transaction_ref = forms.CharField(widget=forms.HiddenInput(), required=False, initial=uuid.uuid4().hex)
    widgets = {
        'title': forms.Select(attrs={'class': 'form-select'}),
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
        'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
        'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        'gender': forms.Select(attrs={'class': 'form-select'}),
        'category': forms.Select(attrs={'class': 'form-select', 'id': 'category-select'}),
        'gand_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GAND Number', 'id': 'gand-number'}),
        'prof_of_status': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        'profession': forms.Select(attrs={'class': 'form-select'}),
        'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization Name'}),
        'about_us': forms.Select(attrs={'class': 'form-select'}),
        'complaince': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        gand_number = cleaned_data.get('gand_number')
        name = cleaned_data.get('name')

        if category in ['GAND Student', 'GAND Full Member']:
            if not gand_number:
                raise ValidationError("GAND number is required for this category.")
            if not validate_gand_number(gand_number, name):
                raise ValidationError("GAND number and name do not match our records.")

        # No validation needed for other categories
        return cleaned_data
