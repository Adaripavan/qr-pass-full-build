import os
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def generate_qr_for_pass(interview_pass, request):
    # The verify URL
    verify_url = request.build_absolute_uri(f'/verify/{interview_pass.secure_token}/')
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f'qr_{interview_pass.pass_id}.png'
    
    interview_pass.qr_image.save(file_name, File(buffer), save=True)
    return interview_pass

def send_pass_email(interview_pass):
    subject = "Interview Invitation & Access Pass"
    
    # HTML template context
    context = {
        'candidate': interview_pass.candidate,
        'interview': interview_pass.interview,
        'pass_id': interview_pass.pass_id,
        'qr_url': interview_pass.qr_image.url if interview_pass.qr_image else '',
    }
    
    html_content = render_to_string('interview_pass/email/pass_email.html', context)
    text_content = render_to_string('interview_pass/email/pass_email.txt', context)
    
    try:
        msg = EmailMultiAlternatives(
            subject, 
            text_content, 
            settings.DEFAULT_FROM_EMAIL, 
            [interview_pass.candidate.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
        interview_pass.email_status = 'SENT'
    except Exception as e:
        interview_pass.email_status = 'FAILED'
        print(f"Failed to send email: {e}")
        
    interview_pass.save()
    return interview_pass.email_status == 'SENT'
