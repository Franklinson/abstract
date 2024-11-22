from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users
from django.contrib.auth import get_user_model


Users = get_user_model()


class UsersCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    confirm_email = forms.EmailField(required=True, label="Confirm Email")  # New confirm email field

    class Meta:
        model = Users
        fields = ('email', 'confirm_email', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')

        if email and confirm_email:
            if email != confirm_email:
                raise forms.ValidationError("Emails do not match!")
        
        return cleaned_data



class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.TextInput(attrs={'readonly': 'readonly'}),
        }