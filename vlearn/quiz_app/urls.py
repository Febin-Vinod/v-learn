from django.urls import path
from . import views

# app_name = 'quiz_app'

urlpatterns = [
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('<int:course_id>/create/', views.create_quiz, name='create_quiz'),
    path('<int:course_id>/quizzes/', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/add_question/', views.add_question, name='add_question'),
    path('course/<int:course_id>/take-quiz/', views.quiz_student_list, name='quiz_student_list'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz_result/<int:quiz_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/<int:quiz_id>/manage_questions/', views.manage_questions, name='manage_questions'),
    
    # Other URL patterns...
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),




]
