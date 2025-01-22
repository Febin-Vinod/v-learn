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
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None

        context = {
            'course': course,
            'is_enrolled': is_enrolled,
            'enrollment': enrollment,  # Add this line
        }
        return render(request, 'course_detail.html', context)
    
def send_enrollment_email(student, course):
    """
    Sends an email to the student when they successfully enroll in a course.
    """
    subject = f"Enrollment Successful: {course.title}"
    message = f"Dear {student.profile.full_name},\n\nYou have successfully enrolled in the course: {course.title}.\n\nBest Regards,\nV-le@rn"
    recipient_email = student.email

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Ensure you have this in settings
            [recipient_email],
            fail_silently=False,
        )
        print("Enrollment email sent successfully")
        print(f"Sending email to: {student.email}")
    except Exception as e:
        print(f"Error sending email: {e}")

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

                    # Send enrollment email to the student
                    send_enrollment_email(request.user, course)


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