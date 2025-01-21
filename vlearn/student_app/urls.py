from django.urls import path
from .views import BrowseCoursesView, EnrollCourseView, MyCoursesView

urlpatterns = [
    path('browse/', BrowseCoursesView.as_view(), name='browse_courses'),
    path('enroll/<int:course_id>/', EnrollCourseView.as_view(), name='enroll_course'),
    path('my_courses/', MyCoursesView.as_view(), name='my_courses'),
]
