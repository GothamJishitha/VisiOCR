from django.shortcuts import render, redirect
import pytesseract
from PIL import Image
import re
from datetime import datetime, timedelta
from io import BytesIO
import qrcode
import base64
from .forms import VisitorPassForm

# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image):
    try:
        img = Image.open(image)
        extracted_text = pytesseract.image_to_string(img)
        return extracted_text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def match_details(text):
    aadhaar_pattern = r"\b\d{4}\s\d{4}\s\d{4}\b"
    dob_pattern = r"\b(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/(?:19|20)\d{2}\b"
    gender_pattern = r"\b(?:Male|Female|Othere|FEMALE|MALE|OTHERRS)\b"

    aadhaar_number = re.search(aadhaar_pattern, text).group() if re.search(aadhaar_pattern, text) else None
    dob = re.search(dob_pattern, text).group() if re.search(dob_pattern, text) else None
    gender = re.search(gender_pattern, text).group() if re.search(gender_pattern, text) else None

    return aadhaar_number, dob, gender

def validate_visit_date(visit_date):
    current_date = datetime.now().date()
    return visit_date > current_date + timedelta(days=1)

def generate_qr_code(visitor_pass):
    # Generate QR code content
    pass_details = f"Pass ID: {visitor_pass.visitor_pass_id}\n" \
                   f"Name: {visitor_pass.name}\n" \
                   f"Mobile Number: {visitor_pass.mobile_number}\n" \
                   f"Date of Visiting: {visitor_pass.date_of_visiting}\n" \
                   f"Duration of Visiting: {visitor_pass.duration_of_visiting} hours\n" \
                   f"Aadhaar Number: {visitor_pass.aadhaar_number}\n" \
                   f"Date of Birth: {visitor_pass.dob}\n" \
                   f"Gender: {visitor_pass.gender}\n"

    # Set status based on date of visiting
    if visitor_pass.date_of_visiting < datetime.now().date():
        pass_status = "Inactive"
    else:
        pass_status = "Active"

    pass_details += f"Pass Status: {pass_status}"

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(pass_details)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Convert image to bytes for HTML rendering
    buffer = BytesIO()
    img.save(buffer)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def home(request):
    if request.method == 'POST':
        form = VisitorPassForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract details from the form
            visitor_pass = form.save(commit=False)
            aadhaar_image = form.cleaned_data['aadhaar_image']

            # Extract Aadhaar details from the image
            extracted_text = extract_text(aadhaar_image)
            aadhaar_number, dob, gender = match_details(extracted_text)

            if aadhaar_number is None:
                form.add_error('aadhaar_image', 'Aadhaar number could not be extracted from the image.')
                return render(request, 'home/home.html', {'form': form})

            # Validate visit date
            if not validate_visit_date(visitor_pass.date_of_visiting):
                form.add_error('date_of_visiting', 'Date of visiting must be at least 24 hours ahead of the current date.')
                return render(request, 'home/home.html', {'form': form})

            # Set additional fields
            visitor_pass.visitor_pass_id = datetime.now().strftime('%Y%m%d%H%M%S')
            visitor_pass.aadhaar_number = aadhaar_number
            if dob:
                visitor_pass.dob = datetime.strptime(dob, '%d/%m/%Y').date()  # Convert to date object
            else:
                form.add_error('aadhaar_image', 'Failed to extract date of birth from Aadhaar image.')
                return render(request, 'home/home.html', {'form': form})

            if gender:
                visitor_pass.gender = gender
            else:
                form.add_error('aadhaar_image', 'Failed to extract gender from Aadhaar image.')
                return render(request, 'home/home.html', {'form': form})

            # Save to the database
            visitor_pass.save()

            # Generate QR code
            qr_code = generate_qr_code(visitor_pass)

            return render(request, 'home/visitor_pass.html', {'visitor_pass': visitor_pass, 'qr_code': qr_code})

    else:
        form = VisitorPassForm()

    return render(request, 'home/home.html', {'form': form})