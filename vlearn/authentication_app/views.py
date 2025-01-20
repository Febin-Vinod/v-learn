from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Instructor, Student, Admin
from django.views import View
from rest_framework.views import APIView
from django.http import HttpResponse


def generate_jwt_tokens(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Register Views
class RegisterInstructor(View):
    def get(self, request):
        return render(request, 'register_instructor.html')

    def post(self, request):
        # Print POST data to debug
        print(f"POST data: {request.POST}")
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        qualification = request.POST.get('qualification')
        bio = request.POST.get('bio')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Check if username is being passed correctly
        print(f"Username: {username}")

        if not username:
            return HttpResponse("Username is required", status=400)

        user = User.objects.create_user(username=username, password=password)
        Instructor.objects.create(
            user=user, full_name=full_name, qualification=qualification,
            bio=bio, phone=phone, address=address
        )

        return redirect('login')




class RegisterStudent(View):
    def get(self, request):
        return render(request, 'register_student.html')

    def post(self, request):
        # Retrieve form data directly, matching the form field names
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        roll_number = request.POST.get('roll_number')
        course = request.POST.get('course')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Check if the username is provided
        if not username:
            return HttpResponse("Username is required", status=400)

        # Create the User and Student objects
        user = User.objects.create_user(username=username, password=password)
        Student.objects.create(
            user=user, full_name=full_name, roll_number=roll_number,
            course=course, phone=phone, address=address
        )

        return redirect('login')  # Redirect to the login page after successful registration


class RegisterAdmin(View):
    def get(self, request):
        return render(request, 'register_admin.html')

    def post(self, request):
        # Debug print statement to check POST data
        print(f"POST data: {request.POST}")

        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        department = request.POST.get('department')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if not username:
            return HttpResponse("Username is required", status=400)

        # Ensure password is also set
        if not password:
            return HttpResponse("Password is required", status=400)

        # Create the user and admin objects
        user = User.objects.create_user(username=username, password=password, is_staff=True)
        Admin.objects.create(
            user=user, full_name=full_name, department=department, 
            phone=phone, address=address
        )

        return redirect('login')




# Login View
class LoginView(APIView):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username:
            return Response({"detail": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({"detail": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user:
            try:
                # Check if user is a student
                student = Student.objects.get(user=user)
                return redirect(f'{reverse("home")}?message=Welcome Student {student.full_name}')
            except Student.DoesNotExist:
                # Check if user is an instructor
                try:
                    instructor = Instructor.objects.get(user=user)
                    return redirect(f'{reverse("home")}?message=Welcome Instructor {instructor.full_name}')
                except Instructor.DoesNotExist:
                    # Check if user is an admin
                    try:
                        admin = Admin.objects.get(user=user)
                        return redirect(f'{reverse("home")}?message=Welcome Admin {admin.full_name}')
                    except Admin.DoesNotExist:
                        # Handle case where the user is not recognized (should never happen)
                        return redirect(reverse('home'))

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
# Home Page or Dashboard
class HomePageView(APIView):
    def get(self, request):
        # Retrieve message from query parameters (URL parameters)
        message = request.GET.get('message', '')
        return render(request, 'home.html', {'message': message})
    
    
# Logout
class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')
