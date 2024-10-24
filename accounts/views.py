from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UsersCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout


def home(request):
    return render(request, 'home.html')


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

    return render(request, 'register.html', {'form': form})


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
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')  # Redirect to login or homepage
