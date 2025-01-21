from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from .models import Course, Enrollment
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


class BrowseCoursesView(View):
    @csrf_exempt
    def get(self, request):
        # Check if the logged-in user has a profile and is a student
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.isStudent:
            return redirect('browse_courses')  # Redirect to a home page or a page for unauthorized users

        courses = Course.objects.all()
        return render(request, 'browse_courses.html', {'courses': courses})

class EnrollCourseView(View):
    @csrf_exempt
    def get(self, request, course_id):
        # Ensure the user is a student before enrolling
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.isStudent:
            return redirect('home')  # Redirect to a page for unauthorized users

        course = get_object_or_404(Course, id=course_id)
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        if created:
            return redirect('my_courses')
        return render(request, 'enroll_error.html', {'course': course})

class MyCoursesView(View):
    @csrf_exempt
    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user)
        return render(request, 'my_courses.html', {'enrollments': enrollments})
