import uuid
import json
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Register
import os

def load_gand_data():
    try:
        with open(settings.BASE_DIR / 'gand_data.json', 'r') as file:
            return json.load(file)  # Returns a list of dictionaries if JSON is valid
    except json.JSONDecodeError as e:
        print("Error loading JSON file:", e)  # Log the error for debugging
        return []  # Return an empty list if JSON fails to load

def validate_gand_number(gand_number, name):
    gand_data = load_gand_data()
    if not isinstance(gand_data, list):
        raise TypeError("GAND data should be a list of dictionaries.")
    
    for entry in gand_data:
        if isinstance(entry, dict) and entry.get('GAND_number') == gand_number and entry.get('name') == name:
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
        
        # Validate GAND number if required for the selected category
        if category in ['GAND Member', 'Student']:
            if not gand_number:
                raise ValidationError("GAND number is required for this category.")
            if not validate_gand_number(gand_number, name):
                raise ValidationError("GAND number and name do not match our records.")
