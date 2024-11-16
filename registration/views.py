import requests
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse
from .models import Register
from django.contrib import messages
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.mail import EmailMessage, EmailMultiAlternatives
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
from .models import EmailLog
from django.contrib.auth.decorators import login_required



# @login_required(login_url='login')
def send_registration_email(registration):
    # Generate QR code with registrant information
    qr_info = f"""
    Name: {registration.name}
    Email: {registration.email}
    Phone: {registration.phone}
    Category: {registration.category}
    Transaction Reference: {registration.transaction_ref}
    """
    qr_code = generate_qr_code(qr_info)

    # Create PDF with QR code
    pdf_file = generate_pdf_ticket(registration, qr_code)

    # Render the external HTML file
    context = {
        'name': registration.name,
        'email': registration.email,
        'category': registration.category,
        'transaction_ref': registration.transaction_ref,
        'site_url': 'https://yourorganization.com',  # Replace with your actual site URL
        'year': datetime.datetime.now().year,
    }
    html_content = render_to_string('email/registration_email.html', context)
    text_content = strip_tags(html_content)  # Fallback plain text version

    # Create and send the email
    subject = "Registration Successful"
    email = EmailMultiAlternatives(
        subject,
        text_content,  # Plain text content
        settings.DEFAULT_FROM_EMAIL,
        [registration.email],
    )

    EmailLog.objects.create(
                recipient=[registration.email],
                subject=subject,
                plain_message=text_content,
                html_message=html_content,
            )
    
    email.attach_alternative(html_content, "text/html")  # Attach HTML content
    email.attach('ticket.pdf', pdf_file.getvalue(), 'application/pdf')  # Attach the PDF ticket
    email.send()


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def generate_pdf_ticket(registration, qr_code):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 12)

    # Add text
    c.drawString(100, 800, "Event Registration Ticket")
    c.drawString(100, 780, f"Name: {registration.name}")
    c.drawString(100, 760, f"Email: {registration.email}")
    c.drawString(100, 740, f"Category: {registration.category}")
    c.drawString(100, 720, f"Transaction Reference: {registration.transaction_ref}")

    # Convert QR code BytesIO to ImageReader
    qr_code.seek(0)  # Reset buffer position
    qr_image = ImageReader(qr_code)

    # Add QR code to PDF
    c.drawImage(qr_image, 100, 600, width=100, height=100)

    # Finalize PDF
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


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
    transaction_ref = request.GET.get('trxref') or request.GET.get('reference')
    session_transaction_ref = request.session.get('transaction_ref')
    form_data = request.session.get('form_data')

    if transaction_ref and session_transaction_ref == transaction_ref:
        if verify_payment(transaction_ref):
            if form_data:
                # Get the amount paid from the verification response
                verification_data = requests.get(
                    f'https://api.paystack.co/transaction/verify/{transaction_ref}',
                    headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
                ).json()
                amount_paid = verification_data['data'].get('amount', 0) / 100  # Convert to currency

                # Save the registration to the database
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
                registration.save()

                # Generate and send the email with the QR code and PDF ticket
                send_registration_email(registration)

                # Clear session data
                del request.session['form_data']
                del request.session['transaction_ref']

                return redirect('author_dashboard')
            else:
                return HttpResponse("Form data not found in session.", status=404)
        else:
            return HttpResponse("Payment verification failed.", status=400)
    else:
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