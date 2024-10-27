from django import forms
from django.forms import inlineformset_factory
from .models import *

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


class ReviewerForm(forms.ModelForm):
    class Meta:
        model = Reviewer
        fields = ['full_name', 'expertise_area']
        widgets = {
            'expertise_area': forms.Select(attrs={'class': 'form-control'}),
        }

    # Optional: Customize labels, add CSS classes, etc.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['abstract', 'reviewer', 'status']
        widgets = {
            'abstract': forms.Select(attrs={'class': 'form-control'}),
            'reviewer': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['abstract'].queryset = self.fields['abstract'].queryset.select_related('track')
        self.fields['reviewer'].queryset = self.fields['reviewer'].queryset.select_related('expertise_area')



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = [
            'title', 'content', 'relevance', 'quality', 'clarity',
            'methods', 'structure', 'data_collection', 'result',
            'conclusion', 'status', 'comment', 'attachment', 'presentation'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'presentation': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        scoring_fields = [
            'title', 'content', 'relevance', 'quality', 'clarity', 
            'methods', 'structure', 'data_collection', 'result', 'conclusion'
        ]
        for field in scoring_fields:
            self.fields[field].widget = forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10})

        # <td><a class="btn btn-sm btn-danger" href="{% url 'assign_reviewers' abstract.id %}" >Assign Reviewers</a></td>
        # <th>Assign</th>