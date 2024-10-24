from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import AbstractForm, AuthorInformationFormSet, PresenterInformationFormSet
from .models import Abstract
import uuid

def create_abstract(request):
    if request.method == 'POST':
        abstract_form = AbstractForm(request.POST, request.FILES)
        author_formset = AuthorInformationFormSet(request.POST)
        presenter_formset = PresenterInformationFormSet(request.POST)

        if (abstract_form.is_valid() and
                author_formset.is_valid() and
                presenter_formset.is_valid()):
            
            # Save the abstract
            abstract = abstract_form.save(commit=False)
            abstract.user = request.user  # Set the user as the current user
            
            # Generate a unique ID starting with 'COND-'
            unique_id = f'COND-{uuid.uuid4().hex[:8].upper()}'  # First 8 characters of UUID
            abstract.abstract_id = unique_id  # Assuming you have an abstract_id field in your model
            abstract.save()

            # Save authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Prepare and send email
            send_mail(
                subject='Abstract Submission Confirmation',
                message=f'Thank you for your submission! Your abstract ID is {unique_id}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],  # Send to the current user
                fail_silently=False,
            )

            return redirect('home')  # Redirect to a success page

    else:
        abstract_form = AbstractForm()
        author_formset = AuthorInformationFormSet()
        presenter_formset = PresenterInformationFormSet()

    return render(request, 'create_abstract.html', {
        'abstract_form': abstract_form,
        'author_formset': author_formset,
        'presenter_formset': presenter_formset,
    })
