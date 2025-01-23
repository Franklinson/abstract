import json
from django.core.mail import send_mail, mail_admins
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from .tasks import schedule_reminders, cancel_reminders, send_email_task


@login_required(login_url='login')
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
            abstract.save()
            abstract_form.save_m2m()

            # Save authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Render email context
            user_email_context = {
                'abstract': {
                    'submission_id': abstract.submission_id,
                    'abstract_title': abstract.abstract_title,
                    'abstract': abstract.abstract,
                    'status': abstract.status,
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                }
            }
            admin_email_context = {'abstract': abstract, 'user': request.user}

            # Send user confirmation email via Celery
            send_email_task.delay(
                email_type='user',
                subject='Abstract Submission Confirmation',
                recipient=request.user.email,
                template_name='emails/user_confirmation_email.html',
                context=user_email_context,
                is_admin=False
            )

            # Send admin notification email via Celery
            send_email_task.delay(
                email_type='admin',
                subject='New Abstract Submission',
                recipient=None,  # Not required for mail_admins
                template_name='emails/admin_notification_email.html',
                context=admin_email_context,
                is_admin=True
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




@login_required(login_url='login')
def edit_abstract(request, id):
    abstract = get_object_or_404(Abstract, id=id)

    if abstract.status in ["Submitted", "Accepted"]:
        messages.warning(request, "This abstract cannot be edited as it is under review or accepted.")
        return redirect('author_dashboard')

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
            abstract_form.save_m2m()

            # Save the formsets for authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Serialize abstract object to dictionary
            user_email_context = {
                'abstract': {
                    'submission_id': abstract.submission_id,
                    'abstract_title': abstract.abstract_title,
                    'abstract': abstract.abstract,
                    'status': abstract.status,
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                }
            }

            # Send confirmation email asynchronously via Celery
            send_email_task.delay(
                email_type='user',
                subject='Abstract Updated Successfully',
                recipient=request.user.email,
                template_name='emails/abstract_update_confirmation.html',
                context=user_email_context,
                is_admin=False
            )

            return redirect('author_dashboard')

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





@login_required(login_url='login')
def delete_abstract(request, id):
    abstract = get_object_or_404(Abstract, id=id)

    if request.method == 'POST':
        # Store email-related details before deleting the abstract
        user_email_context = {'abstract': abstract}
        user_email = request.user.email

        # Delete the abstract and associated data
        abstract.delete()

        # Send confirmation email asynchronously via Celery
        send_email_task.delay(
            email_type='user',
            subject='Abstract Deleted Successfully',
            recipient=user_email,
            template_name='emails/abstract_delete_confirmation.html',
            context=user_email_context,
            is_admin=False
        )

        messages.success(request, 'Abstract and associated data deleted successfully.')
        return redirect('author_dashboard')

    return render(request, 'abstract/confirm_delete.html', {'abstract': abstract})



@login_required(login_url='login')
def abstract_detail(request, id):
    abstract = get_object_or_404(Abstract, id=id)
    return render(request, 'abstract/abstract_detail.html', {'abstract': abstract})




@login_required(login_url='login')
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


@login_required(login_url='login')
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
@login_required(login_url='login')
def assign_reviewers(request, abstract_id):
    abstract = get_object_or_404(Abstract, id=abstract_id)

    matching_reviewers = Reviewer.objects.filter(
        expertise_area=abstract.track
    ).exclude(email=abstract.user)

    reviewer_data = [
        {
            'reviewer': reviewer,
            'assigned_count': Assignment.objects.filter(reviewer=reviewer).count()
        }
        for reviewer in matching_reviewers
    ]

    if request.method == 'POST':
        reviewer_ids = request.POST.getlist('reviewer_ids')
        reviewers_to_assign = Reviewer.objects.filter(id__in=reviewer_ids)

        for reviewer in reviewers_to_assign:
            assignment, created = Assignment.objects.get_or_create(abstract=abstract, reviewer=reviewer)

            if created:
                schedule_reminders(assignment)

            # Serialize email_context explicitly
            email_context = {
                'abstract': {
                    'submission_id': str(abstract.submission_id),
                    'abstract_title': str(abstract.abstract_title),
                    'abstract': str(abstract.abstract),
                    'status': str(abstract.status),
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'reviewer': {
                    'full_name': str(reviewer.full_name),
                    'expertise_area': str(reviewer.expertise_area.track_name),
                    'email': str(reviewer.email.email),
                },
            }

            # Send assignment notification email asynchronously
            send_email_task.delay(
                email_type='reviewer',
                subject='New Abstract Assigned for Review',
                recipient=reviewer.email.email,
                template_name='emails/reviewer_assignment_notification.html',
                context=email_context,
                is_admin=False
            )

        abstract.status = 'Submitted'
        abstract.save()

        messages.success(request, 'Reviewers assigned and abstract status updated to Submitted.')
        return redirect('manager')

    return render(request, 'abstract/assign_reviewers.html', {
        'abstract': abstract,
        'reviewer_data': reviewer_data,
    })





@login_required(login_url='login')
def add_review(request, abstract_id):
    # Get the abstract based on the provided ID
    abstract = get_object_or_404(Abstract, id=abstract_id)
    authors = abstract.authors.all()
    presenters = abstract.presentor.all()
    reviewer = Reviewer.objects.all()

    # Ensure the user is a reviewer
    if not hasattr(request.user, 'reviewer'):
        return redirect('author_dashboard')  # Redirect if not a reviewer

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the review instance without committing
            review = form.save(commit=False)
            review.user = request.user
            review.reviewer = request.user.reviewer
            review.abstract = abstract
            abstract.status = 'Reviewed'
            abstract.save()
            review.save()  # Save the review instance

            # Cancel scheduled reminders for this assignment
            assignment = Assignment.objects.get(abstract=abstract, reviewer=request.user.reviewer)
            cancel_reminders.delay(assignment)
            assignment.is_completed = True
            assignment.save()

            # 1. Send confirmation email to the abstract's author
            author_email_context = {
                'abstract': {
                    'submission_id': str(abstract.submission_id),
                    'user': str(abstract.user.username),
                    'abstract_title': str(abstract.abstract_title),
                    'abstract': str(abstract.abstract),
                    'status': str(abstract.status),
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'reviewer': request.user.reviewer,
                # 'review': review
            }
            send_email_task.delay(
                email_type='author',
                subject='Review Added to Your Abstract',
                recipient=abstract.user.email,
                template_name='emails/review_added_notification.html',
                context=author_email_context,
                is_admin=False
            )

            # 2. Send confirmation email to the reviewer
            reviewer_email_context = {
                'abstract': {
                    'submission_id': str(abstract.submission_id),
                    'user': str(abstract.user.username),
                    'abstract_title': str(abstract.abstract_title),
                    'abstract': str(abstract.abstract),
                    'status': str(abstract.status),
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'review': review,
                'reviewer': {
                    'full_name': str(reviewer.full_name),
                    'expertise_area': str(reviewer.expertise_area.track_name),
                    'email': str(reviewer.email.email),
                },
            }
            send_email_task.delay(
                email_type='reviewer',
                subject='Review Submission Confirmation',
                recipient=request.user.email,
                template_name='emails/reviewer_confirmation_notification.html',
                context=reviewer_email_context,
                is_admin=False
            )

            return redirect('author_dashboard')
    else:
        form = ReviewForm()

    # Render the template with context
    context = {
        'abstract': abstract,
        'form': form,
        'authors':authors,
        'presenters':presenters
    }
    return render(request, 'abstract/add_review.html', context)





@login_required(login_url='login')
def edit_review(request, review_id):
    review = get_object_or_404(Reviews, id=review_id)
    authors = review.abstract.authors.all()
    presenters = review.abstract.presentor.all()

    if review.reviewer.email != request.user:
        return redirect('author_dashboard')

    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('author_dashboard')
    else:
        form = ReviewForm(instance=review)

    
    context = {
        'abstract': review.abstract,
        'form': form,
        'authors': authors,
        'presenters': presenters,

    }
    return render(request, 'abstract/edit_review.html', context)



@login_required(login_url='login')
def manager_create_abstract(request):
    if request.method == 'POST':
        abstract_form = ManagerAbstractForm(request.POST, request.FILES)
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
            abstract_form.save_m2m()

            # Save authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Send confirmation email asynchronously
            user_email_context = {
                'abstract': {
                    'submission_id': abstract.submission_id,
                    'abstract_title': abstract.abstract_title,
                    'abstract': abstract.abstract,
                    'status': abstract.status,
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                }
            }
            send_email_task.delay(
                email_type='user',
                subject='Abstract Submission Confirmation',
                recipient=request.user.email,
                template_name='emails/user_confirmation_email.html',
                context=user_email_context,
                is_admin=False
            )

            return redirect('manager')

    else:
        abstract_form = ManagerAbstractForm()
        author_formset = AuthorInformationFormSet()
        presenter_formset = PresenterInformationFormSet()

    return render(request, 'abstract/manager_create_abstract.html', {
        'abstract_form': abstract_form,
        'author_formset': author_formset,
        'presenter_formset': presenter_formset,
    })




@login_required(login_url='login')
def manager_edit_abstract(request, id):
    abstract = get_object_or_404(Abstract, id=id)

    AuthorInformationFormSet = inlineformset_factory(Abstract, AuthorInformation, form=AuthorInformationForm, extra=1, can_delete=True)
    PresenterInformationFormSet = inlineformset_factory(Abstract, PresenterInformation, form=PresenterInformationForm, extra=1, can_delete=True)

    if request.method == 'POST':
        abstract_form = ManagerAbstractForm(request.POST, request.FILES, instance=abstract)
        author_formset = AuthorInformationFormSet(request.POST, instance=abstract)
        presenter_formset = PresenterInformationFormSet(request.POST, instance=abstract)

        if abstract_form.is_valid() and author_formset.is_valid() and presenter_formset.is_valid():
            # Update the abstract
            abstract = abstract_form.save(commit=False)
            abstract.save()
            abstract_form.save_m2m()

            # Save the formsets for authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Send confirmation email asynchronously
            user_email_context = {
                'abstract': {
                    'submission_id': abstract.submission_id,
                    'abstract_title': abstract.abstract_title,
                    'abstract': abstract.abstract,
                    'status': abstract.status,
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                }
            }

            send_email_task.delay(
                email_type='user',
                subject='Abstract Updated Successfully',
                recipient=request.user.email,
                template_name='emails/abstract_update_confirmation.html',
                context=user_email_context,
                is_admin=False
            )

            return redirect('manager')

    else:
        # Pre-fill the forms with existing data
        abstract_form = ManagerAbstractForm(instance=abstract)
        author_formset = AuthorInformationFormSet(instance=abstract)
        presenter_formset = PresenterInformationFormSet(instance=abstract)

    return render(request, 'abstract/manager_edit_abstract.html', {
        'abstract_form': abstract_form,
        'author_formset': author_formset,
        'presenter_formset': presenter_formset,
        'abstract': abstract,
    })




@login_required(login_url='login')
def manager_add_review(request, abstract_id):
    # Get the abstract based on the provided ID
    abstract = get_object_or_404(Abstract, id=abstract_id)
    authors = abstract.authors.all()
    presenters = abstract.presentor.all()
    reviewer = Reviewer.objects.all()

    if request.method == 'POST':
        form = ManagerReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the review instance without committing
            review = form.save(commit=False)
            review.user = request.user
            review.abstract = abstract
            review.save()  # Save the review instance

            # 1. Send confirmation email to the abstract's author
            author_email_context = {
                'abstract': {
                    'submission_id': str(abstract.submission_id),
                    'user': str(abstract.user.username),
                    'abstract_title': str(abstract.abstract_title),
                    'abstract': str(abstract.abstract),
                    'status': str(abstract.status),
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'reviewer': request.user.reviewer,
                # 'review': review
            }
            send_email_task.delay(
                email_type='author',
                subject='Review Added to Your Abstract',
                recipient=abstract.user.email,
                template_name='emails/review_added_notification.html',
                context=author_email_context,
                is_admin=False
            )

            # 2. Send confirmation email to the reviewer
            reviewer_email_context = {
                'abstract': {
                    'submission_id': str(abstract.submission_id),
                    'user': str(abstract.user.username),
                    'abstract_title': str(abstract.abstract_title),
                    'abstract': str(abstract.abstract),
                    'status': str(abstract.status),
                    'date_created': abstract.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'review': review,
                'reviewer': {
                    'full_name': str(reviewer.full_name),
                    'expertise_area': str(reviewer.expertise_area.track_name),
                    'email': str(reviewer.email.email),
                },
            }
            send_email_task.delay(
                email_type='reviewer',
                subject='Review Submission Confirmation',
                recipient=request.user.email,
                template_name='emails/reviewer_confirmation_notification.html',
                context=reviewer_email_context,
                is_admin=False
            )

            return redirect('manager')

    else:
        form = ManagerReviewForm()

    # Render the template with context
    context = {
        'abstract': abstract,
        'form': form,
        'authors': authors,
        'presenters': presenters,
    }
    return render(request, 'abstract/manager_add_review.html', context)





@login_required(login_url='login')
def manager_edit_review(request, review_id):
    # Get the existing review
    review = get_object_or_404(Reviews, id=review_id)
    authors = review.abstract.authors.all()
    presenters = review.abstract.presentor.all()

    # Ensure the user is the reviewer who created this review
    # if review.reviewer.email != request.user:
    #     return redirect('author_dashboard')  # Redirect if not authorized

    # Initialize the form with the review instance
    if request.method == 'POST':
        form = ManagerReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()  # Directly save the form with updates
            return redirect('manager')  # Redirect after successful submission
    else:
        form = ManagerReviewForm(instance=review)  # Pre-fill form with existing review data

    # Render the template with context
    context = {
        'abstract': review.abstract,  # Pass the associated abstract for context
        'form': form,
        'authors': authors,
        'presenters':presenters,
    }
    return render(request, 'abstract/nanager_edit_review.html', context)