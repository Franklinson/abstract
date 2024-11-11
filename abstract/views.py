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

            # Save authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Render email content from templates
            user_subject = 'Abstract Submission Confirmation'
            user_html_message = render_to_string('emails/user_confirmation_email.html', {
                'abstract': abstract
            })
            user_plain_message = strip_tags(user_html_message)

            send_mail(
                subject=user_subject,
                message=user_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=user_html_message,
                fail_silently=False,
            )

            EmailLog.objects.create(
                recipient=request.user.email,
                subject=user_subject,
                plain_message=user_plain_message,
                html_message=user_html_message,
                abstract=abstract,
            )

            # Send notification email to admins
            admin_subject = 'New Abstract Submission'
            admin_html_message = render_to_string('emails/admin_notification_email.html', {
                'abstract': abstract,
                'user': request.user
            })
            admin_plain_message = strip_tags(admin_html_message)

            mail_admins(
                subject=admin_subject,
                message=admin_plain_message,
                html_message=admin_html_message,
                fail_silently=False,
            )

            EmailLog.objects.create(
                recipient=request.user.email,
                subject=admin_subject,
                plain_message=admin_plain_message,
                html_message=admin_html_message,
                abstract=abstract,
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
        messages.warning(request, "This abstract cannot be edited as it has been submitted or accepted.")
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

            # Save the formsets for authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Render email content from template
            user_subject = 'Abstract Updated Successfully'
            user_html_message = render_to_string('emails/abstract_update_confirmation.html', {
                'abstract': abstract
            })
            user_plain_message = strip_tags(user_html_message)  # Strip HTML tags for plain text version

            # Send confirmation email on edit
            send_mail(
                subject=user_subject,
                message=user_plain_message,  # Plain text message with tags removed
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=user_html_message,  # HTML message
                fail_silently=False,
            )

            EmailLog.objects.create(
                recipient=request.user.email,
                subject=user_subject,
                plain_message=user_plain_message,
                html_message=user_html_message,
                abstract=abstract,
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
        # Delete the abstract and associated authors/presenters (if cascading)
        abstract.delete()

        # Render email content from template
        user_subject = 'Abstract Deleted Successfully'
        user_html_message = render_to_string('emails/abstract_delete_confirmation.html', {
            'abstract': abstract
        })
        user_plain_message = strip_tags(user_html_message)  # Plain text version

        # Send confirmation email on delete
        send_mail(
            subject=user_subject,
            message=user_plain_message,  # Plain text message with tags removed
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            html_message=user_html_message,  # HTML message
            fail_silently=False,
        )

        EmailLog.objects.create(
                recipient=request.user.email,
                subject=user_subject,
                plain_message=user_plain_message,
                html_message=user_html_message,
                abstract=abstract,
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
    # Fetch the abstract
    abstract = get_object_or_404(Abstract, id=abstract_id)

    # Get reviewers with matching expertise, excluding the submitter
    matching_reviewers = Reviewer.objects.filter(
        expertise_area=abstract.track
    ).exclude(email=abstract.user)

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

            # Prepare and send an email to the reviewer
            reviewer_subject = 'New Abstract Assigned for Review'
            reviewer_html_message = render_to_string('emails/reviewer_assignment_notification.html', {
                'abstract': abstract,
                'reviewer': reviewer
            })
            reviewer_plain_message = strip_tags(reviewer_html_message)  # Strip tags for plain text version

            send_mail(
                subject=reviewer_subject,
                message=reviewer_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reviewer.email],
                html_message=reviewer_html_message,
                fail_silently=False,
            )

            EmailLog.objects.create(
                recipient=request.user.email,
                subject=reviewer_subject,
                plain_message=reviewer_plain_message,
                html_message=reviewer_html_message,
                abstract=abstract,
            )

        # Update the abstract's status to 'Submitted'
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

    # Ensure the user is a reviewer
    if not hasattr(request.user, 'reviewer'):
        return redirect('author_dashboard')  # Redirect if not a reviewer

    # Initialize the form
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

            # 1. Send confirmation email to the abstract's author
            author_subject = 'Review Added to Your Abstract'
            author_html_message = render_to_string('emails/review_added_notification.html', {
                'abstract': abstract,
                'reviewer': request.user.reviewer,
                'review': review
            })
            author_plain_message = strip_tags(author_html_message)

            send_mail(
                subject=author_subject,
                message=author_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[abstract.user.email],
                html_message=author_html_message,
                fail_silently=False,
            )

            # Log the email to the author
            EmailLog.objects.create(
                recipient=abstract.user.email,
                subject=author_subject,
                plain_message=author_plain_message,
                html_message=author_html_message,
                abstract=abstract,
            )

            # 2. Send confirmation email to the reviewer
            reviewer_subject = 'Review Submission Confirmation'
            reviewer_html_message = render_to_string('emails/reviewer_confirmation_notification.html', {
                'abstract': abstract,
                'review': review,
                'reviewer': request.user.reviewer,
            })
            reviewer_plain_message = strip_tags(reviewer_html_message)

            send_mail(
                subject=reviewer_subject,
                message=reviewer_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=reviewer_html_message,
                fail_silently=False,
            )

            # Log the email to the reviewer
            EmailLog.objects.create(
                recipient=request.user.email,
                subject=reviewer_subject,
                plain_message=reviewer_plain_message,
                html_message=reviewer_html_message,
                abstract=abstract,
            )

            return redirect('author_dashboard')
    else:
        form = ReviewForm()

    # Render the template with context
    context = {
        'abstract': abstract,
        'form': form,
    }
    return render(request, 'abstract/add_review.html', context)




@login_required(login_url='login')
def edit_review(request, review_id):
    # Get the existing review
    review = get_object_or_404(Reviews, id=review_id)

    # Ensure the user is the reviewer who created this review
    if review.reviewer.email != request.user:
        return redirect('author_dashboard')  # Redirect if not authorized

    # Initialize the form with the review instance
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()  # Directly save the form with updates
            return redirect('author_dashboard')  # Redirect after successful submission
    else:
        form = ReviewForm(instance=review)  # Pre-fill form with existing review data

    # Render the template with context
    context = {
        'abstract': review.abstract,  # Pass the associated abstract for context
        'form': form,
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

            # Save authors and presenters
            author_formset.instance = abstract
            author_formset.save()
            presenter_formset.instance = abstract
            presenter_formset.save()

            # Render email content from templates
            user_subject = 'Abstract Submission Confirmation'
            user_html_message = render_to_string('emails/user_confirmation_email.html', {
                'abstract': abstract
            })
            user_plain_message = strip_tags(user_html_message)

            send_mail(
                subject=user_subject,
                message=user_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=user_html_message,
                fail_silently=False,
            )

            EmailLog.objects.create(
                recipient=request.user.email,
                subject=user_subject,
                plain_message=user_plain_message,
                html_message=user_html_message,
                abstract=abstract,
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

    # if abstract.status in ["Submitted", "Accepted"]:
    #     messages.warning(request, "This abstract cannot be edited as it has been submitted or accepted.")
    #     return redirect('author_dashboard')

    # Inline formsets for authors and presenters
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

            # Save the formsets for authors and presenters
            author_formset.instance = abstract
            author_formset.save()

            presenter_formset.instance = abstract
            presenter_formset.save()

           # Render email content from template
            user_subject = 'Abstract Updated Successfully'
            user_html_message = render_to_string('emails/abstract_update_confirmation.html', {
                'abstract': abstract
            })
            user_plain_message = strip_tags(user_html_message)  # Strip HTML tags for plain text version

            # Send confirmation email on edit
            send_mail(
                subject=user_subject,
                message=user_plain_message,  # Plain text message with tags removed
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=user_html_message,  # HTML message
                fail_silently=False,
            )

            EmailLog.objects.create(
                recipient=request.user.email,
                subject=user_subject,
                plain_message=user_plain_message,
                html_message=user_html_message,
                abstract=abstract,
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

    # Ensure the user is a reviewer
    # if not hasattr(request.user, 'reviewer'):
    #     return redirect('author_dashboard')  # Redirect if not a reviewer

    # Initialize the form
    if request.method == 'POST':
        form = ManagerReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the review instance without committing
            review = form.save(commit=False)
            review.user = request.user 
            # review.reviewer = request.user.reviewer 
            review.abstract = abstract 
            review.save()  # Save the review instance
            return redirect('manager') 
        
        # 1. Send confirmation email to the abstract's author
        author_subject = 'Review Added to Your Abstract'
        author_html_message = render_to_string('emails/review_added_notification.html', {
            'abstract': abstract,
            'reviewer': request.user.reviewer,
            'review': review
        })
        author_plain_message = strip_tags(author_html_message)  # Plain text version

        send_mail(
            subject=author_subject,
            message=author_plain_message,  # Plain text message
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[abstract.user.email],
            html_message=author_html_message,  # HTML message
            fail_silently=False,
        )

        EmailLog.objects.create(
                recipient=request.user.email,
                subject=author_subject,
                plain_message=author_plain_message,
                html_message=author_html_message,
                abstract=abstract,
            )

        # 2. Send confirmation email to the reviewer
        reviewer_subject = 'Review Submission Confirmation'
        reviewer_html_message = render_to_string('emails/reviewer_confirmation_notification.html', {
            'abstract': abstract,
            'review': review,
            'reviewer': request.user.reviewer,
        })
        reviewer_plain_message = strip_tags(reviewer_html_message)  # Plain text version

        send_mail(
            subject=reviewer_subject,
            message=reviewer_plain_message,  # Plain text message
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            html_message=reviewer_html_message,  # HTML message
            fail_silently=False,
        )

        EmailLog.objects.create(
                recipient=request.user.email,
                subject=reviewer_subject,
                plain_message=reviewer_plain_message,
                html_message=reviewer_html_message,
                abstract=abstract,
            )

    else:
        form = ManagerReviewForm()

    # Render the template with context
    context = {
        'abstract': abstract,
        'form': form,
    }
    return render(request, 'abstract/manager_add_review.html', context)




@login_required(login_url='login')
def manager_edit_review(request, review_id):
    # Get the existing review
    review = get_object_or_404(Reviews, id=review_id)

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
    }
    return render(request, 'abstract/nanager_edit_review.html', context)