from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from .models import Enrollment
from instructor.models import Course
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
import razorpay
from django.conf import settings
from django.http import JsonResponse
import json
from django.core.mail import send_mail

class BrowseCoursesView(LoginRequiredMixin,View):
    @csrf_exempt
    def get(self, request):
        # Check if the logged-in user has a profile and is a student
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.isStudent:
            return redirect('home')  # Redirect to a home page or a page for unauthorized users

        courses = Course.objects.all()
        return render(request, 'browse_courses.html', {'courses': courses})


class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Ensure the logged-in user is a student
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.isStudent:
            return render(request, 'home.html', status=403)

        # Fetch enrolled courses and grades for the student
        enrollments = Enrollment.objects.filter(student=request.user)
        # grades = Grade.objects.filter(student=request.user)

        context = {
            'enrollments': enrollments,  # List of courses the student is enrolled in
            # 'grades': grades,            # List of grades for the student
        }

        return render(request, 'student_dashboard.html', context)
    

class CourseDetailView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        # Ensure the logged-in user is a student
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.isStudent:
            return render(request, 'unauthorized.html', status=403)

        # Get the course details
        course = get_object_or_404(Course, id=course_id)

        # Check if the user is already enrolled in the course
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()


        context = {
            'course': course,
            'is_enrolled': is_enrolled,
        }
        return render(request, 'course_detail.html', context)
    


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def course_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    print(course.price)
    
    # Create Razorpay order
    order_amount = int(round(course.price * 100))   # Razorpay expects the amount in paise
    order_currency = 'INR'
    print(order_amount)
    order = client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'payment_capture': '1'
    })
    
    razorpay_key = settings.RAZORPAY_KEY_ID
    return render(request, 'payment.html', {
        'course': course,
        'razorpay_key': razorpay_key,
        'order_id': order['id'],
        'order_amount': order_amount,
    })


def confirm_payment(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            course_id = data.get('course_id')
            
            # Verify the payment with Razorpay
            payment = client.payment.fetch(payment_id)
            print(f"Payment Status: {payment['status']}")  # Log the payment status

            if payment['status'] == 'authorized':
                # Capture the payment
                capture_response = client.payment.capture(payment_id, payment['amount'])
                
                
                # If capture is successful, proceed with enrollment
                if capture_response['status'] == 'captured':
                    # Enroll the student in the course
                    course = get_object_or_404(Course, id=course_id)
                    Enrollment.objects.create(student=request.user, course=course)

                    # Send enrollment confirmation email
                    try:
                        subject = f"Enrollment Confirmation for {course.title}"
                        message = (
                            f"Dear {request.user.profile.full_name},\n\n"
                            f"You have successfully enrolled in the course: {course.title}.\n\n"
                            f"Course Details:\n"
                            f"Instructor: {course.instructor}\n"
                            f"Duration: {course.duration}\n"
                            f"Price: {course.price}\n\n"
                            f"Thank you for choosing our platform!\n"
                        )
                        recipient_email = request.user.email

                        send_mail(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,  # Sender's email
                            [recipient_email],
                            fail_silently=False,
                        )
                    except Exception as email_error:
                        print(f"Error sending email: {email_error}")

                    return JsonResponse({'success': True, 'message': 'Enrollment successful'})
                else:
                    return JsonResponse({'success': False, 'message': 'Payment capture failed'})
            else:
                return JsonResponse({'success': False, 'message': 'Payment not authorized'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'success': False, 'message': 'Payment verification failed'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def payment_success(request, course_id):
    # Fetch the course details
    course = get_object_or_404(Course, id=course_id)
    
    # Optionally, you can fetch additional data, such as enrollment details
    # enrollment = Enrollment.objects.get(student=request.user, course=course)
    
    context = {
        'course': course,
    }
    return render(request, 'success.html', context)