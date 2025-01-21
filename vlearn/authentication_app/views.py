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

        if not username:
            return HttpResponse("Username is required", status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        Instructor.objects.create(
            user=user,
            full_name=full_name,
            qualification=qualification,
            bio=bio,
            phone=phone,
            address=address
        )

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

        if not username:
            return HttpResponse("Username is required", status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        Student.objects.create(
            user=user,
            full_name=full_name,
            school=school,
            phone=phone,
            address=address
        )

        return redirect('login1') 


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return HttpResponse("Both username and password are required.", status=400)

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)

            if user.is_staff:
                return redirect(f'{reverse("home")}')

            profile = getattr(user, 'profile', None)

            if profile and profile.isStudent:
                return redirect(f'{reverse("browse_courses")}?message=Welcome Student {profile.full_name}')
            elif profile and profile.isInstructor:
                return redirect(f'{reverse("home")}?message=Welcome Instructor {profile.full_name}')
            else:
                return redirect(f'{reverse("home")}?message=Welcome {user.username}')
        return HttpResponse("Invalid credentials", status=401)


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
        
    