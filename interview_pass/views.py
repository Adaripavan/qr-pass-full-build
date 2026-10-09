import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Interview, Candidate, InterviewPass, ScanLog
from .forms import InterviewUploadForm
from .utils import generate_qr_for_pass, send_pass_email
import pandas as pd
import openpyxl

def dashboard(request):
    total_candidates = Candidate.objects.count()
    total_passes = InterviewPass.objects.count()
    emails_sent = InterviewPass.objects.filter(email_status='SENT').count()
    emails_failed = InterviewPass.objects.filter(email_status='FAILED').count()
    
    recent_passes = InterviewPass.objects.all().order_by('-created_at')[:10]
    
    if request.method == 'POST':
        form = InterviewUploadForm(request.POST, request.FILES)
        if form.is_valid():
            interview = form.save()
            file = request.FILES.get('candidate_file')
            
            # Single Candidate Data
            single_name = form.cleaned_data.get('candidate_name')
            single_email = form.cleaned_data.get('candidate_email')
            single_role = form.cleaned_data.get('candidate_role')
            
            success_count = 0
            
            try:
                # 1. Process Bulk Upload
                if file:
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                    elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                        df = pd.read_excel(file)
                    else:
                        messages.error(request, 'Unsupported file format. Please upload CSV or Excel.')
                        return redirect('dashboard')
                    
                    # Make column parsing smarter
                    df.columns = df.columns.str.strip().str.lower()
                    col_map = {}
                    for col in df.columns:
                        if 'email' in col or 'mail' in col:
                            col_map[col] = 'email'
                        elif 'name' in col:
                            col_map[col] = 'name'
                        elif 'role' in col:
                            col_map[col] = 'role'
                    df.rename(columns=col_map, inplace=True)
                    
                    required_cols = ['name', 'email', 'role']
                    if not all(col in df.columns for col in required_cols):
                        messages.error(request, 'Could not detect required columns. Please use "Name", "Email", and "Role" as headers.')
                        return redirect('dashboard')
                    
                    for _, row in df.iterrows():
                        candidate, _ = Candidate.objects.get_or_create(
                            email=row['email'],
                            name=row['name'],
                            defaults={'role': row['role']}
                        )
                        interview_pass = InterviewPass.objects.create(candidate=candidate, interview=interview)
                        generate_qr_for_pass(interview_pass, request)
                        send_pass_email(interview_pass)
                        success_count += 1
                
                # 2. Process Single Candidate if provided
                if single_name and single_email and single_role:
                    candidate, _ = Candidate.objects.get_or_create(
                        email=single_email,
                        name=single_name,
                        defaults={'role': single_role}
                    )
                    interview_pass = InterviewPass.objects.create(candidate=candidate, interview=interview)
                    generate_qr_for_pass(interview_pass, request)
                    send_pass_email(interview_pass)
                    success_count += 1
                    
                if success_count == 0:
                    messages.error(request, 'Please upload a file OR fill in the single candidate details.')
                    interview.delete() # cleanup empty interview
                    return redirect('dashboard')
                    
                messages.success(request, f'Successfully generated and sent {success_count} interview passes!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error processing data: {str(e)}')
                return redirect('dashboard')
    else:
        form = InterviewUploadForm()
        
    context = {
        'total_candidates': total_candidates,
        'total_passes': total_passes,
        'emails_sent': emails_sent,
        'emails_failed': emails_failed,
        'recent_passes': recent_passes,
        'form': form
    }
    return render(request, 'interview_pass/dashboard.html', context)

def resend_email(request, pk):
    interview_pass = get_object_or_404(InterviewPass, pk=pk)
    success = send_pass_email(interview_pass)
    if success:
        messages.success(request, f'Email resent successfully to {interview_pass.candidate.name}')
    else:
        messages.error(request, f'Failed to resend email to {interview_pass.candidate.name}. Check SMTP settings.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

def bulk_resend_email(request):
    if request.method == 'POST':
        pass_ids = request.POST.getlist('pass_ids')
        if not pass_ids:
            messages.warning(request, 'No candidates selected.')
            return redirect('candidates_list')
        
        success_count = 0
        passes = InterviewPass.objects.filter(id__in=pass_ids)
        for p in passes:
            if send_pass_email(p):
                success_count += 1
                
        messages.success(request, f'Successfully sent {success_count} emails out of {len(pass_ids)} selected.')
    return redirect('candidates_list')

def bulk_delete_passes(request):
    if request.method == 'POST':
        pass_ids = request.POST.getlist('pass_ids')
        if not pass_ids:
            messages.warning(request, 'No candidates selected.')
            return redirect('candidates_list')
        
        passes = InterviewPass.objects.filter(id__in=pass_ids)
        count = passes.count()
        passes.delete()
        messages.success(request, f'Successfully deleted {count} passes.')
    return redirect('candidates_list')

def candidates_list(request):
    passes = InterviewPass.objects.all().order_by('-created_at')
    return render(request, 'interview_pass/candidates.html', {'passes': passes})

def candidate_detail(request, pk):
    interview_pass = get_object_or_404(InterviewPass, pk=pk)
    
    # Passes are usually ordered by -created_at (newest first).
    # ID is a good proxy for creation order. 
    # Next = older (id < current), Prev = newer (id > current)
    next_pass = InterviewPass.objects.filter(id__lt=interview_pass.id).order_by('-id').first()
    prev_pass = InterviewPass.objects.filter(id__gt=interview_pass.id).order_by('id').first()
    
    context = {
        'interview_pass': interview_pass,
        'next_pass': next_pass,
        'prev_pass': prev_pass
    }
    return render(request, 'interview_pass/candidate_detail.html', context)

def qr_pass_view(request, pk):
    interview_pass = get_object_or_404(InterviewPass, pk=pk)
    return render(request, 'interview_pass/qr_pass.html', {'interview_pass': interview_pass})

def verify_pass(request, token):
    try:
        interview_pass = InterviewPass.objects.get(secure_token=token)
    except InterviewPass.DoesNotExist:
        return render(request, 'interview_pass/verify_result.html', {
            'status': 'INVALID',
            'message': 'Invalid Interview Pass',
            'sub_message': 'Access cannot be granted. Token not found.'
        })

    # Log the scan
    client_ip = request.META.get('REMOTE_ADDR')
    
    # Check statuses
    if interview_pass.status == 'CANCELLED':
        ScanLog.objects.create(interview_pass=interview_pass, result='CANCELLED', ip_address=client_ip)
        return render(request, 'interview_pass/verify_result.html', {
            'status': 'CANCELLED',
            'interview_pass': interview_pass,
            'message': 'Pass Cancelled',
            'sub_message': 'This pass has been cancelled by HR.'
        })

    if interview_pass.status == 'USED':
        ScanLog.objects.create(interview_pass=interview_pass, result='ALREADY_USED', ip_address=client_ip)
        return render(request, 'interview_pass/verify_result.html', {
            'status': 'USED',
            'interview_pass': interview_pass,
            'message': 'Pass Already Used',
            'sub_message': f'This pass was already scanned at {interview_pass.scanned_at.strftime("%d %b %Y, %I:%M %p") if interview_pass.scanned_at else "an unknown time"}.'
        })
        
    # Check if expired based on date (assuming pass is valid only on interview date)
    if interview_pass.interview.date < timezone.now().date():
        interview_pass.status = 'EXPIRED'
        interview_pass.save()
        ScanLog.objects.create(interview_pass=interview_pass, result='EXPIRED', ip_address=client_ip)
        return render(request, 'interview_pass/verify_result.html', {
            'status': 'EXPIRED',
            'interview_pass': interview_pass,
            'message': 'Interview Pass Expired',
            'sub_message': 'The interview date has passed.'
        })

    # If valid, mark as used and record scan time
    interview_pass.status = 'USED'
    interview_pass.scanned_at = timezone.now()
    interview_pass.save()
    
    ScanLog.objects.create(interview_pass=interview_pass, result='VALID', ip_address=client_ip)
    
    return render(request, 'interview_pass/verify_result.html', {
        'status': 'VALID',
        'interview_pass': interview_pass,
        'message': 'Interview Pass Verified',
        'sub_message': 'Access Approved. Scan logged successfully.'
    })

def security_scanner(request):
    return render(request, 'interview_pass/security_scanner.html')

def scan_history(request):
    logs = ScanLog.objects.all().order_by('-scanned_at')
    return render(request, 'interview_pass/scan_history.html', {'logs': logs})

def bulk_delete_logs(request):
    if request.method == 'POST':
        log_ids = request.POST.getlist('log_ids')
        if not log_ids:
            messages.warning(request, 'No logs selected.')
            return redirect('scan_history')
        
        logs = ScanLog.objects.filter(id__in=log_ids)
        count = logs.count()
        logs.delete()
        messages.success(request, f'Successfully deleted {count} scan logs.')
    return redirect('scan_history')
