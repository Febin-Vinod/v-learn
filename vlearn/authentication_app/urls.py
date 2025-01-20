from django.urls import path
from .views import RegisterInstructor, RegisterStudent, LoginView, HomePageView, LogoutView

urlpatterns = [
    path('register/instructor/', RegisterInstructor.as_view(), name='register_instructor'),
    path('register/student/', RegisterStudent.as_view(), name='register_student'),
    path('home/', HomePageView.as_view(), name='home'),
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
