import requests
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse, JsonResponse
from .models import *
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
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.utils.http import urlencode
from .forms import load_gand_data, validate_gand_number



def send_registration_email(registration):
    qr_code = generate_qr_code(registration)

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

    # Log only the plain text message
    EmailLog.objects.create(
        recipient=[registration.email],
        subject=subject,
        plain_message=strip_tags(html_content),
        html_message=html_content,
    )
    
    email.attach_alternative(html_content, "text/html")  # Attach HTML content
    email.attach('ticket.pdf', pdf_file.getvalue(), 'application/pdf')  # Attach the PDF ticket
    email.send()



def generate_qr_code(registration):
    qr_data = {
        "registration_number": registration.registration_number,
    }
    api_url = f"https://settings.SITE_URL/api/validate_registration/?{urlencode(qr_data)}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(api_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def generate_pdf_ticket(registration, qr_code):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # Dimensions for an 8.5x11 inch page

    # Margins and line settings
    margin_left = 50
    line_height = 20

    # Add Ticket Details (Top)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left, height - 50, f"Ticket ID: {registration.registration_number}")
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, height - 70, f"Order Date: {registration.date_created.strftime('%B %d, %Y')}")
    c.drawString(margin_left, height - 90, f"Order Number: {registration.registration_number.split('-')[-1]}")
    c.drawString(margin_left, height - 110, f"Payment Method: Paystack")

    # Billing Address Section
    c.setFont("Helvetica-Bold", 12)
    # c.drawString(margin_left, height - 150, "Billing Address:")
    c.setFont("Helvetica", 10)
    billing_address = [
        registration.name,
        registration.address,
        "City: ReplaceCity",  # Replace with actual city if available
        "Country: ReplaceCountry",  # Replace with actual country if available
    ]
    y_position = height - 170
    for line in billing_address:
        c.drawString(margin_left, y_position, line)
        y_position -= line_height

    # QR Code Section (Left)
    qr_code.seek(0)  # Reset buffer position
    qr_image = ImageReader(qr_code)
    c.drawImage(qr_image, width - 150, height - 200, width=150, height=150)  # Adjusted for positioning

    # Ticket Table Headers
    table_data = [
        ["Ticket", "Qty", "Price"],  # Header
        [
            f"{registration.category} Participants\nName: {registration.name}\nDate: {registration.date_created.strftime('%B %d, %Y')}\nVenue: Conference Center, City XYZ",
            "1",
            f"{registration.amount_paid:.2f}" if registration.amount_paid else "0.00",
        ],
    ]

    # Add Ticket Table
    table = Table(table_data, colWidths=[300, 50, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, margin_left, y_position - 100)

    # Add Subtotal and Total
    y_position -= 150
    subtotal = f"{registration.amount_paid:.2f}" if registration.amount_paid else "0.00"
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left + 300, y_position, "Subtotal:")
    c.drawString(margin_left + 400, y_position, subtotal)

    # Draw a horizontal line between Subtotal and Total
    y_position -= 10
    c.line(margin_left + 300, y_position, margin_left + 500, y_position)

    # Total
    y_position -= 20
    c.drawString(margin_left + 300, y_position, "Total:")
    c.drawString(margin_left + 400, y_position, subtotal)

    # Finalize PDF
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer



def fetch_member_info(request):
    gand_number = request.GET.get('gand_number')
    gand_data = load_gand_data()

    if gand_number:
        for member in gand_data.get("good_standing", []):
            if member.get("GAND_number") == gand_number:
                return JsonResponse({"success": True, "name": member.get("name"), "standing": "good_standing"})
        for member in gand_data.get("not_in_good_standing", []):
            if member.get("GAND_number") == gand_number:
                return JsonResponse({"success": True, "name": member.get("name"), "standing": "not_in_good_standing"})
        return JsonResponse({"success": False, "message": "GAND number not found."})
    return JsonResponse({"success": False, "message": "GAND number is required."})



def register(request):
    # Pricing logic
    category_prices = {
        "good_standing": {
            "GAND Student": 40,
            "GAND Full Member": 60,
        },
        "not_in_good_standing": {
            "GAND Student": 50,
            "GAND Full Member": 70,
        },
        "fixed_pricing": {
            "Non GAND Member": 90,
            "Non GAND Student": 80,
            "International": 150,
        },
    }

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            gand_number = form.cleaned_data.get('gand_number')
            name = form.cleaned_data.get('name')

            # Determine pricing based on category
            if category in ['GAND Student', 'GAND Full Member']:
                # Validate GAND number and determine standing
                standing = "good_standing" if validate_gand_number(gand_number, name) else "not_in_good_standing"
                price = category_prices[standing].get(category)
            else:
                # Use fixed pricing for other categories
                price = category_prices["fixed_pricing"].get(category)

            if price is None:
                form.add_error('category', "Invalid category selection.")
                return render(request, 'register_form.html', {'form': form, 'category_prices': category_prices})

            amount = price * 100  # Convert to kobo for Paystack

            # Initiate payment with Paystack
            transaction_ref = form.cleaned_data.get('transaction_ref')
            email = form.cleaned_data.get('email')
            paystack_response = initiate_paystack_payment(transaction_ref, email, amount)

            if paystack_response:
                # Store form data in session
                request.session['form_data'] = form.cleaned_data
                request.session['transaction_ref'] = transaction_ref
                return redirect(paystack_response['data']['authorization_url'])
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
    callback_url = f"{settings.SITE_URL}{reverse('paystack_callback')}"
    print(f"Callback URL: {callback_url}")
    payload = {
        'reference': transaction_ref,
        'email': email,
        'amount': amount,
        'callback_url': f"{settings.SITE_URL}{reverse('paystack_callback')}",
          # Set dynamic callback URL
    }
    response = requests.post('https://api.paystack.co/transaction/initialize', json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None



def paystack_callback(request):
    transaction_ref = request.GET.get('trxref') or request.GET.get('reference')
    session_transaction_ref = request.session.get('transaction_ref')
    form_data = request.session.get('form_data')
    print(f"Callback transaction_ref: {transaction_ref}")
    print(f"Session transaction_ref: {session_transaction_ref}")

    if transaction_ref:
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




def validate_coupon(request):
    code = request.GET.get('code')
    total_price = request.GET.get('total_price')

    try:
        total_price = float(total_price)
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "message": "Invalid total price."})

    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid():
            return JsonResponse({"success": False, "message": "Coupon is invalid or expired."})

        if coupon.discount_type == 'percentage':
            discount = total_price * (coupon.discount_value / 100)
        elif coupon.discount_type == 'fixed':
            discount = coupon.discount_value
        else:
            discount = 0

        # Ensure discount doesn't exceed total price
        discount = min(discount, total_price)

        return JsonResponse({"success": True, "discount": discount, "final_price": total_price - discount})
    except Coupon.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invalid coupon code."})
