from django.contrib import admin
from .models import Interview, Candidate, InterviewPass, ScanLog

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('hr_name', 'date', 'time', 'location')
    search_fields = ('hr_name', 'location')
    list_filter = ('date',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'created_at')
    search_fields = ('name', 'email', 'role')

@admin.register(InterviewPass)
class InterviewPassAdmin(admin.ModelAdmin):
    list_display = ('pass_id', 'candidate', 'status', 'email_status', 'created_at')
    search_fields = ('pass_id', 'candidate__name', 'candidate__email')
    list_filter = ('status', 'email_status')

@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('interview_pass', 'result', 'scanned_at')
    list_filter = ('result', 'scanned_at')
