# InterviewPass System

A Django-based HR system to generate, distribute, and verify QR-based interview passes.

## Features
- HR Dashboard with statistics.
- Bulk upload candidates via CSV/Excel.
- Automatic unique QR code generation.
- Automated email dispatch with QR code attachments.
- Security scanner page using device camera.
- Scan history and verification logging.

## Setup Instructions

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure .env**
   - Copy `.env.example` to `.env`
   - Fill in your Gmail App Password for SMTP to work (If left blank, emails will fallback to printing in console).
   ```bash
   copy .env.example .env
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (Optional, for admin panel)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start server**
   ```bash
   python manage.py runserver
   ```

8. **Test the Workflow**
   - Open HR Dashboard: `http://127.0.0.1:8000/`
   - Upload the provided `sample_candidates.csv`.
   - Ensure you configure your `.env` SMTP settings to actually receive the emails.
   - Open Security Scanner: `http://127.0.0.1:8000/security/`

## Example CSV Format (sample_candidates.csv)
```csv
name,email,role
Rahul Kumar,rahul@example.com,Software Engineer
Sneha Reddy,sneha@example.com,QA Engineer
Arjun Mehta,arjun@example.com,Data Analyst
```
