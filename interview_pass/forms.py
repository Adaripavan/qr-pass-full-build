from django import forms
from .models import Interview

class InterviewUploadForm(forms.ModelForm):
    candidate_file = forms.FileField(
        label='Upload Candidate List (CSV/Excel)',
        help_text='Required columns: name, email, role',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv, .xlsx, .xls'}),
        required=False
    )
    
    candidate_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Candidate Name'}))
    candidate_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Candidate Email'}))
    candidate_role = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Role (e.g. Developer)'}))

    class Meta:
        model = Interview
        fields = ['hr_name', 'hr_email', 'hr_contact', 'company_name', 'date', 'time', 'location']
        widgets = {
            'hr_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ananya Rao'}),
            'hr_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. hr@company.com'}),
            'hr_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +91 98765 43210'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TechCorp'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TechCorp Hyderabad'}),
        }
