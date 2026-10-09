from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('candidates/', views.candidates_list, name='candidates_list'),
    path('candidates/bulk-resend/', views.bulk_resend_email, name='bulk_resend_email'),
    path('candidates/bulk-delete/', views.bulk_delete_passes, name='bulk_delete_passes'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('candidates/<int:pk>/qr/', views.qr_pass_view, name='qr_pass_view'),
    path('candidates/<int:pk>/resend/', views.resend_email, name='resend_email'),
    path('verify/<uuid:token>/', views.verify_pass, name='verify_pass'),
    path('security/', views.security_scanner, name='security_scanner'),
    path('history/', views.scan_history, name='scan_history'),
    path('history/bulk-delete/', views.bulk_delete_logs, name='bulk_delete_logs'),
]
