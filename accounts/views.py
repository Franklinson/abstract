from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UsersCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from abstract.models import *


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

            # Success message for the user
            messages.success(request, f'Account was created successfully ')
            return redirect('home')
    else:
        form = UsersCreationForm()

    return render(request, 'account/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back,!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'account/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')  # Redirect to login or homepage



def author_dashboard(request):
    # Get the current user's abstracts (those they submitted)
    abstracts = request.user.abstract_set.all()

    # Check if the user is a reviewer and, if so, retrieve assigned abstracts
    is_reviewer = hasattr(request.user, 'reviewer')  # Checks if the user has a `Reviewer` profile
    assigned_abstracts = Assignment.objects.filter(reviewer=request.user.reviewer) if is_reviewer else []

    # Count the total number of abstracts submitted by the user
    total_abstract = abstracts.count()

    # Count only accepted abstracts by the user
    total_accepted = abstracts.filter(status='Accepted').count()

    # Context for rendering the template
    context = {
        'abstracts': abstracts,
        'total_abstract': total_abstract,
        'total_accepted': total_accepted,
        'is_reviewer': is_reviewer,
        'assigned_abstracts': assigned_abstracts,
    }
    return render(request, 'account/author_dashboard.html', context)
