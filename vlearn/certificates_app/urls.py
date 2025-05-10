from django.urls import path
from . import views

app_name = 'certificates_app'

urlpatterns = [
    path('generate/<int:enrollment_id>/', views.generate_certificate, name='generate_certificate'),
    path('download/<int:enrollment_id>/', views.download_certificate_pdf, name='download_certificate'),
]
