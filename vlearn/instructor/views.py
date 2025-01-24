from django.shortcuts import render, redirect
from .forms import CourseForm, VideoForm, VideoFormSet,CourseUpdateForm
from .models import Course, Category, Video
from authentication_app.models import Instructor, Profile
from student_app.models import Enrollment
from quiz_app.models import Result 
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseForbidden
from authentication_app.decorators import instructor_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.http import HttpResponse  

@instructor_required
@login_required
@csrf_exempt
def add_course(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')

        if category_id == 'others' and new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
            request.POST = request.POST.copy()
            request.POST['category'] = category.id

        course_form = CourseForm(request.POST, request.FILES)
        video_form = VideoForm(request.POST, request.FILES)

        if course_form.is_valid() and video_form.is_valid():
            course = course_form.save(commit=False)

            # Check if the user has an associated Instructor profile
            try:
                profile = Profile.objects.get(user=request.user)
                if not profile.isInstructor:
                    return HttpResponse("You are not an instructor. Please contact the admin.")
                instructor = Instructor.objects.get(pk=profile.pk)  # Get the Instructor instance
                course.instructor = instructor  # Assign the instructor to the course
                course.save()

                video = video_form.save(commit=False)
                video.course = course
                video.save()

                return redirect('my_courses')
            except Profile.DoesNotExist:
                return HttpResponse("You do not have a profile. Please contact the admin.")
            except Instructor.DoesNotExist:
                return HttpResponse("You are not an instructor. Please contact the admin.")
        else:
            print("Course Form Errors:", course_form.errors)
            print("Video Form Errors:", video_form.errors)
    else:
        course_form = CourseForm()
        video_form = VideoForm()

    return render(request, 'add_course.html', {
        'course_form': course_form,
        'video_form': video_form,
    })
@instructor_required
@csrf_exempt
def my_courses(request):
    try:
        # Fetch the Instructor profile associated with the logged-in user
        instructor_profile = Instructor.objects.get(user=request.user)
        
        # Fetch courses belonging to the instructor
        courses = Course.objects.filter(instructor=instructor_profile).prefetch_related('videos', 'category')

        return render(request, 'my_courses.html', {'courses': courses})
    except Instructor.DoesNotExist:
        return HttpResponse("You are not an instructor. Please contact the admin.")


@instructor_required
@csrf_exempt
def add_video(request, course_id):
    # Get the logged-in instructor profile
    try:
        instructor_profile = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        return HttpResponse("You are not an instructor. Please contact the admin.")

    # Get the course associated with the logged-in instructor
    course = get_object_or_404(Course, id=course_id, instructor=instructor_profile)

    # Create a formset for the Video model with no initial queryset
    VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=1, can_delete=False)

    if request.method == 'POST':
        # Handle the submitted formset
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.none())

        if formset.is_valid():
            # Save the formset and assign the course to each video
            for form in formset:
                video = form.save(commit=False)
                video.course = course  # Set the course foreign key
                video.save()

            return HttpResponseRedirect(reverse('my_courses'))  # Redirect after saving the videos
        else:
            print("Formset Errors:", formset.errors)
    else:
        # Provide an empty queryset for the formset to show only new forms
        formset = VideoFormSet(queryset=Video.objects.none())

    return render(request, 'add_video.html', {'formset': formset, 'course': course})


@instructor_required
@csrf_exempt
def instructor_dashboard(request):
    return render(request, 'instructor_dashboard.html', {'instructor': request.user.profile})

    
@login_required
@csrf_exempt
def student_management(request):
    # Get the instructor profile associated with the logged-in user
    instructor_profile = request.user.profile  # Assuming the 'Profile' is linked to the 'User'
    
    # Ensure the user is an instructor
    if not instructor_profile.isInstructor:
        return render(request, 'access_denied.html')  # Redirect to an access-denied page

    # Get all courses that belong to this instructor
    courses = Course.objects.filter(instructor=instructor_profile)

    # Prepare course data with enrolled students and their results
    course_data = []
    for course in courses:
        enrollments = Enrollment.objects.filter(course=course)  # Fetch all enrollments for the course
        print(f"Enrollments for {course.title}: {enrollments.count()}")  # Debugging statement
        
        students_data = []

        for enrollment in enrollments:
            student_profile = enrollment.student.profile  # Get the profile of the student
            
            # Check if the student has taken any quiz in this course
            results = Result.objects.filter(student=student_profile, quiz__course=course)
            print(f"Results for {student_profile.full_name} in {course.title}: {results.count()}")  # Debugging statement
            
            if results.exists():
                # If results exist, show the quiz results
                result = results.first()  # Assuming there's only one result per quiz
                students_data.append({
                    'student': student_profile,
                    'quiz_title': result.quiz.title,
                    'score': f"{result.score}/{result.quiz.questions.count()}",
                    'percentage': result.percentage,
                    'status': result.status,
                })
            else:
                # If no results exist, show "Not Applicable" for quiz details
                students_data.append({
                    'student': student_profile,
                    'quiz_title': "Not Applicable",
                    'score': "Not Applicable",
                    'percentage': "Not Applicable",
                    'status': "Not Applicable",
                })
        
        course_data.append({
            'course': course,
            'students': students_data,
        })
    
    return render(request, 'student_management.html', {
        'instructor': instructor_profile,
        'course_data': course_data,
    })    



@instructor_required
@csrf_exempt
def instructor_management(request):
    # You can limit access to this view to certain instructors if needed
    return render(request, 'instructor_management.html', {'instructor': request.user.profile})
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('my_courses')  # Redirect to the courses list page
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.delete()
    return redirect('my_courses')  # Redirect to the page showing all courses


def update_course(request, course_id):
    # Fetch the course to be updated
    course = get_object_or_404(Course, id=course_id)
    
    # Fetch all categories for the dropdown list
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # If the form is submitted
        form = CourseUpdateForm(request.POST, request.FILES, instance=course)
        
        if form.is_valid():
            updated_course = form.save(commit=False)
            
            # Handle new category if 'others' is selected
            if request.POST.get('category') == 'others':
                new_category = request.POST.get('new_category')
                category, created = Category.objects.get_or_create(name=new_category)
                updated_course.category = category
            
            updated_course.save()
            
            # Redirect to the 'my_courses.html' page after updating
            return redirect('my_courses')  # Assuming 'my_courses' is the name of the URL for the course list page
    
    else:
        # If the request is not POST, render the update page with the course form
        form = CourseUpdateForm(instance=course)
    
    return render(request, 'update.html', {'form': form, 'course': course, 'categories': categories})

def logout_view(request):
    logout(request)
    return redirect('login1')  # Redirect the user to the login page after logout





from django.shortcuts import render, redirect
from room.models import Room
from student_app.models import Enrollment
from django.utils.text import slugify

@instructor_required
@csrf_exempt
def manage_chat_rooms(request):
    try:
        # Get the user's profile
        profile = Profile.objects.get(user=request.user)
        
        # Check if the user is an instructor
        if not profile.isInstructor:
            return HttpResponse("You are not an instructor. Please contact the admin.")
        
        # Get the instructor instance
        instructor = Instructor.objects.get(pk=profile.pk)
        
        # Get courses taught by the instructor
        instructor_courses = Course.objects.filter(instructor=instructor)
        
        # Get chat rooms created by this instructor's profile
        chat_rooms = Room.objects.filter(creator=profile)
        
        if request.method == 'POST':
            course_id = request.POST.get('course')
            room_name = request.POST.get('room_name')
            
            if course_id and room_name:
                course = Course.objects.get(id=course_id)
                
                # Create new chat room
                room = Room.objects.create(
                    name=room_name,
                    slug=slugify(room_name),
                    creator=profile
                )
                
                # Add instructor to participants
                room.participants.add(profile)
                
                # Add enrolled students to participants
                enrollments = Enrollment.objects.filter(course=course)
                for enrollment in enrollments:
                    student_profile = Profile.objects.get(user=enrollment.student)
                    room.participants.add(student_profile)
                
                return redirect('manage_chat_rooms')
        
        context = {
            'instructor_courses': instructor_courses,
            'chat_rooms': chat_rooms
        }
        return render(request, 'instructor/manage_chat_rooms.html', context)
        
    except Profile.DoesNotExist:
        return HttpResponse("You do not have a profile. Please contact the admin.")
    except Instructor.DoesNotExist:
        return HttpResponse("You are not registered as an instructor. Please contact the admin.")