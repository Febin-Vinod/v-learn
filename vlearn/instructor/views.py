from django.shortcuts import render, redirect
from .forms import CourseForm, VideoForm, VideoFormSet
from .models import Course, Category, Video



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
        # Get the category
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')

        if category_id == "others" and new_category_name:
            # Create new category if "others" is selected
            category, created = Category.objects.get_or_create(name=new_category_name)
            request.POST = request.POST.copy()  # Create a writable copy of POST
            request.POST['category'] = category.id

        # Handle the course form
        course_form = CourseForm(request.POST, request.FILES)
        
        # Handle the video formset
        video_formset = VideoFormSet(request.POST, request.FILES)

        if course_form.is_valid() and video_formset.is_valid():
            # Save the course
            course = course_form.save()

            # Save the videos
            for form in video_formset:
                if form.is_valid():  # Check if the form is valid
                    video = form.save(commit=False)
                    video.course = course
                    video.save()

            return redirect('my_courses')  # Redirect to course list after successful submission
        else:
            print(course_form.errors)  # Log form errors for debugging
            print(video_formset.errors)  # Log formset errors for debugging

    else:
        course_form = CourseForm()
        video_formset = VideoFormSet(queryset=Video.objects.none())  # Start with no video forms

    return render(request, 'add_course.html', {
        'course_form': course_form,
        'video_formset': video_formset,
    })



def my_courses(request):
    # Assuming courses can be filtered by the logged-in user
    courses = Course.objects.all()  # Replace with filter for logged-in user if necessary
    
    return render(request, 'my_courses.html', {'courses': courses})



