from django.core.mail import send_mail
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import *
from .models import *
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages





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

    return render(request, 'abstract/create_abstract.html', {
        'abstract_form': abstract_form,
        'author_formset': author_formset,
        'presenter_formset': presenter_formset,
    })



def edit_abstract(request, id):
    abstract = get_object_or_404(Abstract, id=id)

    # Inline formsets for authors and presenters
    AuthorInformationFormSet = inlineformset_factory(Abstract, AuthorInformation, form=AuthorInformationForm, extra=1, can_delete=True)
    PresenterInformationFormSet = inlineformset_factory(Abstract, PresenterInformation, form=PresenterInformationForm, extra=1, can_delete=True)

    if request.method == 'POST':
        abstract_form = AbstractForm(request.POST, request.FILES, instance=abstract)
        author_formset = AuthorInformationFormSet(request.POST, instance=abstract)
        presenter_formset = PresenterInformationFormSet(request.POST, instance=abstract)

        if abstract_form.is_valid() and author_formset.is_valid() and presenter_formset.is_valid():
            # Update the abstract
            abstract = abstract_form.save(commit=False)
            abstract.save()

            # Save the formsets for authors and presenters
            author_formset.instance = abstract
            author_formset.save()

            presenter_formset.instance = abstract
            presenter_formset.save()

            # Send confirmation email on edit
            send_mail(
                subject='Abstract Updated Successfully',
                message=f'Your abstract with ID {abstract.abstract_id} has been updated successfully.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            return redirect('home', id=abstract.id)  # Redirect to abstract detail or another page

    else:
        # Pre-fill the forms with existing data
        abstract_form = AbstractForm(instance=abstract)
        author_formset = AuthorInformationFormSet(instance=abstract)
        presenter_formset = PresenterInformationFormSet(instance=abstract)

    return render(request, 'abstract/edit_abstract.html', {
        'abstract_form': abstract_form,
        'author_formset': author_formset,
        'presenter_formset': presenter_formset,
        'abstract': abstract,
    })



def delete_abstract(request, id):
    abstract = get_object_or_404(Abstract, id=id)

    if request.method == 'POST':
        # Delete the abstract and associated authors/presenters (if cascading)
        abstract.delete()

        # Send confirmation email on delete
        send_mail(
            subject='Abstract Deleted Successfully',
            message=f'Your abstract with ID {abstract.id} has been deleted.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )

        messages.success(request, 'Abstract and associated data deleted successfully.')
        return redirect('home')  # Redirect to the abstract list or another page

    return render(request, 'abstract/confirm_delete.html', {'abstract': abstract})



def abstract_detail(request, id):
    abstract = get_object_or_404(Abstract, id=id)
    return render(request, 'abstract/abstract_detail.html', {'abstract': abstract})