from django.urls import path,include
from .views import RegisterInstructor, RegisterStudent, LoginView, HomePageView, LogoutView, approve_instructors_view
from . import views
urlpatterns = [
    path('', LoginView.as_view(), name='login1'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/instructor/', RegisterInstructor.as_view(), name='register_instructor'),
    path('register/student/', RegisterStudent.as_view(), name='register_student'),
    path('home/', HomePageView.as_view(), name='home'),
    path('approve-instructors/', approve_instructors_view, name="approve_instructors"),
    path('chat/', include('core.urls')), 
]
