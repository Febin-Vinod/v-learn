from django.urls import path
from . import views

# app_name = 'quiz_app'

urlpatterns = [
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('<int:course_id>/create/', views.create_quiz, name='create_quiz'),
    path('<int:course_id>/quizzes/', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/add_question/', views.add_question, name='add_question'),
]
