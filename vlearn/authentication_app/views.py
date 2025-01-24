from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Instructor, Student
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def generate_jwt_tokens(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterInstructor(View):
    def get(self, request):
        return render(request, 'register_instructor.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        qualification = request.POST.get('qualification')
        bio = request.POST.get('bio')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')

        # Validations
        if not all([username, password, full_name, qualification, email]):
            messages.error(request, "All required fields must be filled.")
            return redirect('register_instructor')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('register_instructor')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register_instructor')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register_instructor')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('register_instructor')

        # Create user and instructor
        user = User.objects.create_user(username=username, password=password, email=email)
        Instructor.objects.create(
            user=user,
            full_name=full_name,
            qualification=qualification,
            bio=bio,
            phone=phone,
            address=address
        )
        messages.success(request, "Registration successful. Please login.")
        return redirect('login1')



class RegisterStudent(View):
    def get(self, request):
        return render(request, 'register_student.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        school = request.POST.get('school')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')

        # Validations
        if not all([username, password, full_name, school, email]):
            messages.error(request, "All required fields must be filled.")
            return redirect('register_student')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('register_student')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register_student')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register_student')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('register_student')

        # Create user and student
        user = User.objects.create_user(username=username, password=password, email=email)
        Student.objects.create(
            user=user,
            full_name=full_name,
            school=school,
            phone=phone,
            address=address
        )
        messages.success(request, "Registration successful. Please login.")
        return redirect('login1') 


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validations
        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect('login1')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('home')

            profile = getattr(user, 'profile', None)
            if profile:
                if profile.isStudent:
                    return redirect('browse_courses')
                elif profile.isInstructor:
                    return redirect('instructor_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login1')


class HomePageView(LoginRequiredMixin, View):
    def get(self, request):
        message = request.GET.get('message', '')
        profile = request.user.profile
        context = {
            'message': message,
            'profile': profile
        }
        return render(request, 'home.html', context)


class LogoutView(View):
    def get(self, request):  # Handle GET requests too
        logout(request)
        return redirect('login')  # This will redirect to authentication_app login
        
    