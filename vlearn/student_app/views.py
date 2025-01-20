from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def browse_courses(request):
    # Check if the logged-in user has a profile and is a student
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.isStudent:
        return redirect('home')  # Redirect to a home page or a page for unauthorized users

    courses = Course.objects.all()
    return render(request, 'browse_courses.html', {'courses': courses})

@login_required
def enroll_course(request, course_id):
    # Ensure the user is a student before enrolling
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.isStudent:
        return redirect('home')  # Redirect to a page for unauthorized users

    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        return redirect('my_courses')
    return render(request, 'enroll_error.html', {'course': course})


def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'my_courses.html', {'enrollments': enrollments})
