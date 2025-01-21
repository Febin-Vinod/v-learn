from django.urls import path
from . import views

urlpatterns = [
    path('add-course/', views.add_course, name='add_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
]
