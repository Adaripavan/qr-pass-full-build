import os
from django.core.management.base import BaseCommand
from interview_pass.models import Interview, Candidate, InterviewPass
from interview_pass.utils import generate_qr_for_pass
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with demo HR data and candidates'

    def handle(self, *args, **kwargs):
        # Create Interview
        interview = Interview.objects.create(
            hr_name="Ananya Rao",
            hr_email="hr@techcorp.com",
            hr_contact="+91 98765 43210",
            company_name="TechCorp",
            date=timezone.now().date() + timedelta(days=2),
            time=timezone.datetime.strptime('11:30', '%H:%M').time(),
            location="TechCorp Hyderabad"
        )
        self.stdout.write(self.style.SUCCESS('Created demo interview.'))

        # Create Candidates
        candidates_data = [
            {"name": "Rahul Kumar", "email": "rahul@example.com", "role": "Software Engineer"},
            {"name": "Sneha Reddy", "email": "sneha@example.com", "role": "QA Engineer"},
            {"name": "Arjun Mehta", "email": "arjun@example.com", "role": "Data Analyst"},
        ]

        # Note: In a real environment, we'd pass a dummy request or None to generate_qr_for_pass 
        # But we need a request object to build absolute URI for the QR code.
        # So for a management command, we'll build a dummy request or hardcode the host for the QR.
        # Let's adjust utils.py to handle a None request by falling back to settings or localhost.
        
        for data in candidates_data:
            candidate = Candidate.objects.create(**data)
            ipass = InterviewPass.objects.create(candidate=candidate, interview=interview)
            
            # Generate dummy QR logic since we don't have a real request object here easily
            import qrcode
            from io import BytesIO
            from django.core.files import File
            
            verify_url = f"http://127.0.0.1:8000/verify/{ipass.secure_token}/"
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(verify_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f'qr_{ipass.pass_id}.png'
            ipass.qr_image.save(file_name, File(buffer), save=True)
            ipass.email_status = 'PENDING'
            ipass.save()
            
            self.stdout.write(self.style.SUCCESS(f'Created pass for {candidate.name}.'))
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data!'))
