from django.urls import path
from . import views

urlpatterns = [
    path('add-course/', views.add_course, name='add_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('add_video/<int:course_id>/', views.add_video, name='add_video'), 
    path('courses/my_courses/', views.my_courses, name='my_courses'),
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('student_management/', views.student_management, name='student_management'),
    path('instructor_management/', views.instructor_management, name='instructor_management'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('delete_video/<int:video_id>/', views.delete_video, name='delete_video'),
    path('update_course/<int:course_id>/', views.update_course, name='update_course'),
]
