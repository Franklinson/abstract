from django import forms
from django.forms import inlineformset_factory
from .models import Abstract, AuthorInformation, PresenterInformation

class AbstractForm(forms.ModelForm):
    class Meta:
        model = Abstract
        fields = [
            'abstract_title',
            'abstract',
            'keywords',
            'attachment',
            'track',
            'presentation_type',
        ]

class AuthorInformationForm(forms.ModelForm):
    class Meta:
        model = AuthorInformation
        fields = ['author_name', 'email', 'affiliation']

class PresenterInformationForm(forms.ModelForm):
    class Meta:
        model = PresenterInformation
        fields = ['name', 'email']

# Inline formsets for authors and presenters
AuthorInformationFormSet = inlineformset_factory(
    Abstract, AuthorInformation, form=AuthorInformationForm, extra=1, can_delete=True
)

PresenterInformationFormSet = inlineformset_factory(
    Abstract, PresenterInformation, form=PresenterInformationForm, extra=1, can_delete=True
)
