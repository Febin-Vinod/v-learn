from django.shortcuts import render, redirect
from .forms import CourseForm, VideoForm, VideoFormSet
from .models import Course, Category, Video
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse





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
            course = course_form.save()

            video = video_form.save(commit=False)
            video.course = course
            video.save()

            return redirect('my_courses')
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






def my_courses(request):
    courses = Course.objects.prefetch_related('videos', 'category')  # Optimize queries
    return render(request, 'my_courses.html', {'courses': courses})

def add_video(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Creating formset for the Video model
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
        formset = VideoFormSet(queryset=Video.objects.filter(course=course))

    return render(request, 'add_video.html', {'formset': formset, 'course': course})

def instructor_dashboard(request):
    return render(request, 'instructor_dashboard.html')

def student_management(request):
    # Logic for student management (e.g., list students, manage student data)
    return render(request, 'student_management.html')

def instructor_management(request):
    # Logic for instructor management (e.g., manage instructors)
    return render(request, 'instructor_management.html')
