from django.shortcuts import render, redirect
from .forms import CourseForm, VideoForm, VideoFormSet
from .models import Course, Category, Video
from authentication_app.models import Instructor, Profile
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseForbidden
from authentication_app.decorators import instructor_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.http import HttpResponse  #



# def add_course(request):
#     if request.method == 'POST':
#         category_id = request.POST.get('category')  # Get the selected category
#         new_category_name = request.POST.get('new_category')  # Get the new category name (if any)

#         if category_id == "others" and new_category_name:  # If "Others" is selected and new category is provided
#             # Create the new category or fetch it if it already exists
#             category, created = Category.objects.get_or_create(name=new_category_name)
#             # Replace the "Others" category ID with the new category's ID in the POST data
#             request.POST = request.POST.copy()
#             request.POST['category'] = category.id

#         # Handle the course form
#         course_form = CourseForm(request.POST, request.FILES)
#         video_formset = VideoFormSet(request.POST, request.FILES)  # Initialize the formset for POST requests
        
#         if course_form.is_valid() and video_formset.is_valid():
#             course = course_form.save()  # Save the course first
            
#             # Handle the video formset
#             for form in video_formset:
#                 video = form.save(commit=False)
#                 video.course = course  # Associate the video with the course
#                 video.save()

#             return redirect('my_courses')  # Redirect to the course list after saving
#     else:
#         course_form = CourseForm()  # Handle the empty course form for GET requests
#         video_formset = VideoFormSet(queryset=Video.objects.none())  # Empty formset for new videos

#     return render(request, 'add_course.html', {
#         'course_form': course_form,
#         'video_formset': video_formset,
#     })

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

    # Create a formset for the Video model
    VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=1)

    if request.method == 'POST':
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.filter(course=course))

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
        formset = VideoFormSet(queryset=Video.objects.filter(course=course))

    return render(request, 'add_video.html', {'formset': formset, 'course': course})



@instructor_required
@csrf_exempt
def instructor_dashboard(request):
    return render(request, 'instructor_dashboard.html', {'instructor': request.user.profile})


@instructor_required
@csrf_exempt
def student_management(request):
    # Fetch students related to the logged-in instructor's courses
    courses = Course.objects.filter(instructor=request.user.instructor)
    #students = Student.objects.filter(course__in=courses)  # Assuming there's a relation to a course model
    return render(request, 'student_management.html', {'students': students})

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


def logout_view(request):
    logout(request)
    return redirect('login1')  # Redirect the user to the login page after logout