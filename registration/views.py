import requests
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            transaction_ref = form.cleaned_data.get('transaction_ref')
            if verify_payment(transaction_ref):  # Verify payment before saving
                form.save()
                return redirect('success_page')  # Redirect to a success page
            else:
                form.add_error(None, "Payment verification failed.")
    else:
        form = RegisterForm()
    return render(request, 'register_form.html', {'form': form})






def verify_payment(transaction_ref):
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.get(
        f'https://api.paystack.co/transaction/verify/{transaction_ref}',
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        return data['status'] and data['data']['status'] == 'success'
    return False