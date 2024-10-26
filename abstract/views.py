from django.core.mail import send_mail
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
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
            abstract.user = request.user 
            
            # Generate a unique ID starting with 'COND-'
            unique_id = f'COND-{uuid.uuid4().hex[:8].upper()}'
            abstract.abstract_id = unique_id 
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
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            return redirect('author_dashboard')

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
                message=f'Your abstract with ID {abstract.id} has been updated successfully.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            return redirect('author_dashboard', id=abstract.id)

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
        return redirect('author_dashboard')

    return render(request, 'abstract/confirm_delete.html', {'abstract': abstract})



def abstract_detail(request, id):
    abstract = get_object_or_404(Abstract, id=id)
    return render(request, 'abstract/abstract_detail.html', {'abstract': abstract})



def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = AssignmentForm()

    return render(request, 'abstract/assignment_form.html', {'form': form})



# def create_reviewer(request):
#     if request.method == 'POST':
#         form = ReviewerForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = ReviewerForm()

#     return render(request, 'abstract/reviewer_form.html', {'form': form})


# @login_required
def create_reviewer(request):
    if request.method == 'POST':
        form = ReviewerForm(request.POST)
        if form.is_valid():
            reviewer = form.save(commit=False)
            reviewer.email = request.user 
            reviewer.save()
            return redirect('home')
    else:
        form = ReviewerForm()

    return render(request, 'abstract/reviewer_form.html', {'form': form, 'user_email': request.user.email})


# for the chair
def assign_reviewers(request, abstract_id):
    # Fetch the abstract
    abstract = get_object_or_404(Abstract, id=abstract_id)

    # Get reviewers with matching expertise (same track as the abstract)
    matching_reviewers = Reviewer.objects.filter(expertise_area=abstract.track)

    # Prepare reviewer data with assignment counts
    reviewer_data = [
        {
            'reviewer': reviewer,
            'assigned_count': Assignment.objects.filter(reviewer=reviewer).count()  # Count of abstracts assigned to the reviewer
        }
        for reviewer in matching_reviewers
    ]

    if request.method == 'POST':
        # Retrieve selected reviewers from the form
        reviewer_ids = request.POST.getlist('reviewer_ids')
        reviewers_to_assign = Reviewer.objects.filter(id__in=reviewer_ids)

        # Assign each selected reviewer to the abstract
        for reviewer in reviewers_to_assign:
            Assignment.objects.get_or_create(abstract=abstract, reviewer=reviewer)

        return redirect('author_dashboard') 

    return render(request, 'abstract/assign_reviewers.html', {
        'abstract': abstract,
        'reviewer_data': reviewer_data,
    })