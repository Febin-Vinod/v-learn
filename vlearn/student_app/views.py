from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment
from django.contrib.auth.decorators import login_required

def browse_courses(request):
    courses = Course.objects.all()
    return render(request, 'student_app/browse_courses.html', {'courses': courses})


def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        return redirect('my_courses')
    return render(request, 'student_app/enroll_error.html', {'course': course})


def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'student_app/my_courses.html', {'enrollments': enrollments})
