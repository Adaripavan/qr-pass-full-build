import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone

class Interview(models.Model):
    hr_name = models.CharField(max_length=100)
    hr_email = models.EmailField(blank=True, null=True)
    hr_contact = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hr_name} - {self.date}"

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

class InterviewPass(models.Model):
    STATUS_CHOICES = (
        ('VALID', 'Valid'),
        ('USED', 'Used'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    )
    
    EMAIL_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    )

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='passes')
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='passes')
    pass_id = models.CharField(max_length=20, unique=True, blank=True)
    secure_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VALID')
    email_status = models.CharField(max_length=20, choices=EMAIL_STATUS_CHOICES, default='PENDING')
    scanned_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pass_id} - {self.candidate.name}"

    def save(self, *args, **kwargs):
        if not self.pass_id:
            # Generate a pass ID like IP-2026-8F42A91C
            year = timezone.now().year
            short_uuid = str(self.secure_token).split('-')[0].upper()
            self.pass_id = f"IP-{year}-{short_uuid}"
        
        super().save(*args, **kwargs)

class ScanLog(models.Model):
    interview_pass = models.ForeignKey(InterviewPass, on_delete=models.CASCADE, related_name='scan_logs')
    scanned_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=50) # VALID, USED, EXPIRED, CANCELLED, INVALID
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.interview_pass.pass_id} - {self.result} at {self.scanned_at}"
