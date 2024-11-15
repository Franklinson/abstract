from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UsersCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from abstract.models import *
from django.contrib.auth.decorators import login_required
from registration.models import Register

def home(request):
    return render(request, 'account/home.html')


def register(request):
    if request.method == 'POST':
        form = UsersCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            email = form.cleaned_data.get('email')
            subject = 'Your COND account has been created'
            message = f'Hi,\n\nYour account on COND has been successfully created.\n\nBest regards,\nThe COND Team'

            # Send the confirmation email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, f'Account was created successfully ')
            return redirect('login')
    else:
        form = UsersCreationForm()

    return render(request, 'account/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back,!')
            return redirect('author_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'account/login.html')



@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')


@login_required(login_url='login')
def author_dashboard(request):
    # Get the current user's abstracts and their reviewed abstracts
    abstracts = request.user.abstract_set.all()
    reviews = Reviews.objects.filter(
        user=request.user, 
        status__in=['Reviewed', 'Accept Pending Review', 'Accepted', 'Rejected']
    )

    # Check if the user is a reviewer and fetch only unreviewed assigned abstracts
    is_reviewer = hasattr(request.user, 'reviewer')
    if is_reviewer:
        # Filter for assigned abstracts that haven't been reviewed by the current user
        assigned_abstracts = Assignment.objects.filter(
            reviewer=request.user.reviewer
        ).exclude(
            abstract__in=reviews.values_list('abstract', flat=True)
        )
    else:
        assigned_abstracts = []

    # Count the total number of abstracts and accepted abstracts
    total_abstract = abstracts.count()
    total_accepted = abstracts.filter(status='Accepted').count()
    reviewed_abstracts = reviews

    context = {
        'abstracts': abstracts,
        'total_abstract': total_abstract,
        'total_accepted': total_accepted,
        'is_reviewer': is_reviewer,
        'assigned_abstracts': assigned_abstracts,
        'reviews': reviews,
        'reviewed_abstracts': reviewed_abstracts,
    }
    return render(request, 'account/author_dashboard.html', context)


@login_required(login_url='login')
def manager(request):
    abstracts = Abstract.objects.all()
    reviews = Reviews.objects.all()
    total_abstract = abstracts.count()
    total_accepted = abstracts.filter(status='Accepted').count()
    total_pending = abstracts.filter(status='Pending').count()
    total_rejected = abstracts.filter(status='Rejected').count()
    total_submitted = abstracts.filter(status='Submitted').count()
    total_reviewed = abstracts.filter(status='Reviewed').count()
    register = Register.objects.count()

    reviewed = abstracts.filter(status='Reviewed')
    accepted = abstracts.filter(status='Accepted')

    context = {
        'abstracts': abstracts,
        'total_abstract': total_abstract,
        'total_accepted': total_accepted,
        'total_pending': total_pending,
        'total_rejected': total_rejected,
        'total_submitted': total_submitted,
        'total_reviewed': total_reviewed,
        'reviewed': reviewed,
        'accepted': accepted,
        'reviews': reviews,
        'register': register,
    }
    return render(request, 'account/overseer_dashboard.html', context)
