from django import forms
from .models import Register
import uuid

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = [
            'title', 'name', 'email', 'address', 'phone', 'gender', 'category',
            'gand_number', 'prof_of_status', 'profession', 'organization', 'about_us', 'complaince'
        ]
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'gand_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GAND Number'}),
            'prof_of_status': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'profession': forms.Select(attrs={'class': 'form-select'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization Name'}),
            'about_us': forms.Select(attrs={'class': 'form-select'}),
            'complaince': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # transaction_ref = forms.CharField(widget=forms.HiddenInput(), required=False, initial=uuid.uuid4().hex)