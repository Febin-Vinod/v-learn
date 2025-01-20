from django.urls import path
from .views import RegisterInstructor, RegisterStudent, RegisterAdmin, LoginView,HomePageView

urlpatterns = [
    path('register/instructor/', RegisterInstructor.as_view(), name='register_instructor'),
    path('register/student/', RegisterStudent.as_view(), name='register_student'),
    path('register/admin/', RegisterAdmin.as_view(), name='register_admin'),
    path('home/', HomePageView.as_view(), name='home'),  # Mapping 'home' URL to HomePageView
    path('login/', LoginView.as_view(), name='login'),
]
