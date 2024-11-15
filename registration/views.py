import requests
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse
from .models import Register
from django.contrib import messages
from django.urls import reverse
# from .forms import GAND_DATA



# def fetch_gand_name(request):
#     gand_number = request.GET.get('gand_number')
#     gand_name = GAND_DATA.get(gand_number, "")
#     return JsonResponse({'name': gand_name})


def register(request):
    category_prices = {
        'Student': 50,
        'GAND Member': 70,
        'Non GAND Member': 100,
        'International': 150,
    }

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # Determine the payment amount based on the category
            category = form.cleaned_data.get('category')
            amount = category_prices.get(category) * 100  # Convert to kobo for Paystack

            # Initiate payment with Paystack
            transaction_ref = form.cleaned_data.get('transaction_ref')
            email = form.cleaned_data.get('email')
            paystack_response = initiate_paystack_payment(transaction_ref, email, amount)

            if paystack_response:
                # Store form data in session for temporary storage
                request.session['form_data'] = form.cleaned_data
                request.session['transaction_ref'] = transaction_ref
                return redirect(paystack_response['data']['authorization_url'])  # Redirect to Paystack payment page
            else:
                form.add_error(None, "Failed to initiate payment. Please try again.")
    else:
        form = RegisterForm()

    return render(request, 'register_form.html', {'form': form, 'category_prices': category_prices})





# Helper function to initiate Paystack payment
def initiate_paystack_payment(transaction_ref, email, amount):
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'reference': transaction_ref,
        'email': email,
        'amount': amount,
        'callback_url': f"{settings.SITE_URL}{reverse('paystack_callback')}",  # Set dynamic callback URL
    }
    response = requests.post('https://api.paystack.co/transaction/initialize', json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None



def paystack_callback(request):
    # Retrieve transaction reference from the callback URL
    transaction_ref = request.GET.get('trxref') or request.GET.get('reference')
    session_transaction_ref = request.session.get('transaction_ref')
    form_data = request.session.get('form_data')

    # Debugging outputs to confirm data at each step
    print("Callback URL hit with transaction_ref:", transaction_ref)
    print("Session transaction_ref:", session_transaction_ref)
    print("Form data in session:", form_data)

    # Ensure both references match and verify the payment
    if transaction_ref and session_transaction_ref == transaction_ref:
        if verify_payment(transaction_ref):
            if form_data:
                # Get the amount paid from the verification response
                verification_data = requests.get(
                    f'https://api.paystack.co/transaction/verify/{transaction_ref}',
                    headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
                ).json()

                amount_paid = verification_data['data'].get('amount', 0) / 100  # Convert from kobo to currency

                # Delete session data after successful retrieval
                del request.session['form_data']
                del request.session['transaction_ref']
                
                # Save the form data to the database
                registration = Register(
                    title=form_data.get('title'),
                    name=form_data.get('name'),
                    email=form_data.get('email'),
                    address=form_data.get('address'),
                    phone=form_data.get('phone'),
                    gender=form_data.get('gender'),
                    category=form_data.get('category'),
                    gand_number=form_data.get('gand_number'),
                    prof_of_status=form_data.get('prof_of_status'),
                    profession=form_data.get('profession'),
                    organization=form_data.get('organization'),
                    about_us=form_data.get('about_us'),
                    complaince=form_data.get('complaince'),
                    transaction_ref=transaction_ref,
                    amount_paid=amount_paid
                )
                
                # Attempt to save the registration
                try:
                    registration.save()
                    return redirect('author_dashboard')
                except Exception as e:
                    print("Error saving registration:", e)
                    messages.error(request, "Error saving registration.")
                    return HttpResponse("Error saving registration.", status=500)
            else:
                print("Form data not found in session.")
                return HttpResponse("Form data not found in session.", status=404)
        else:
            print("Payment verification failed.")
            return HttpResponse("Payment verification failed.", status=400)
    else:
        print("Transaction reference mismatch or missing.")
        return HttpResponse("Bad Request: Transaction reference mismatch.", status=400)


def verify_payment(transaction_ref):
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.get(f'https://api.paystack.co/transaction/verify/{transaction_ref}', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Paystack verification data:", data)  # Debugging output
        # Check if both the root-level 'status' is True and 'data.status' is 'success'
        if data.get('status') is True and data['data'].get('status') == 'success':
            return True
    print("Paystack verification failed with status code:", response.status_code)
    return False