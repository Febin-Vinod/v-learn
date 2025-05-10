from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .models import Certificate
from student_app.models import Enrollment
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from quiz_app.models import Quiz, Result
from authentication_app.models import Student

@login_required
def generate_certificate(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    user=request.user

    # Check if the student passed the quiz
    quiz = Quiz.objects.filter(course=enrollment.course).first()
    if not quiz:
        return HttpResponseForbidden("No quiz available for this course.")
    student = Student.objects.get(user=user)
    result = Result.objects.filter(student=student, quiz=quiz, status="Passed").first()

    if not result:
        return HttpResponseForbidden("You must pass the quiz to generate a certificate.")
    
    # Create certificate if it doesn't exist
    certificate, created = Certificate.objects.get_or_create(
        student=request.user,
        course=enrollment.course,
        enrollment=enrollment
    )
    
    context = {
        'certificate': certificate,
        'student_name': request.user.profile.full_name,
        'course_name': enrollment.course.title,
        'issue_date': certificate.issue_date,
        'certificate_id': certificate.certificate_id,
        'pdf_download': False
    }
    
    return render(request, 'certificates_app/view_certificate.html', context)

@login_required
def download_certificate_pdf(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    certificate = get_object_or_404(Certificate, enrollment=enrollment)
    
    template = get_template('certificates_app/view_certificate.html')
    context = {
        'certificate': certificate,
        'student_name': request.user.profile.full_name,
        'course_name': enrollment.course.title,
        'issue_date': certificate.issue_date,
        'certificate_id': certificate.certificate_id,
        'pdf_download': True  # This will hide the download button in PDF
    }
    
    html = template.render(context)
    result = BytesIO()
    
    # Configure PDF options
    pdf_options = {
        'page-size': 'Letter',
        'orientation': 'Landscape',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
    }
    
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result,
        options=pdf_options
    )
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=certificate_{certificate.certificate_id}.pdf'
        return response
    return HttpResponse('Error generating PDF', status=400)