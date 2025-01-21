from django.urls import path
from . import views
from .views import BrowseCoursesView, StudentDashboardView, CourseDetailView

urlpatterns = [
    path('browse/', BrowseCoursesView.as_view(), name='browse_courses'),
    path('dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('course/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:course_id>/payment/', views.course_payment, name='course_payment'),
    path('confirm_payment/', views.confirm_payment, name='confirm_payment'),
    path('payment/success/<int:course_id>/', views.payment_success, name='payment_success'),
]
