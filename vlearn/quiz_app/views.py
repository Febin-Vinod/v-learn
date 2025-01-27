from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Choice,Result
from instructor.models import Course  # Assuming 'instructor_app' is where your course model resides
from .forms import QuizForm, QuestionForm, ChoiceForm
from django.http import HttpResponse
from authentication_app.models import Profile, Instructor,Student 
# Create Quiz View
# Create Quiz View
@login_required
def create_quiz(request, course_id):
    try:
        # Get the Profile for the logged-in user
        profile = Profile.objects.get(user=request.user)

        # Check if the user is an instructor
        if not profile.isInstructor:
            return HttpResponse("You are not an instructor. Please contact the admin.")
        
        # Get the Instructor instance using the profile's primary key
        instructor = Instructor.objects.get(pk=profile.pk)

    except Profile.DoesNotExist:
        return HttpResponse("Profile not found. Please contact the admin.")
    except Instructor.DoesNotExist:
        return HttpResponse("Instructor not found. Please contact the admin.")

    # Ensure the course exists and is owned by the logged-in instructor
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the course is owned by the logged-in instructor
    if course.instructor != instructor:
        # If the course is not owned by the logged-in instructor, redirect to an error page
        messages.error(request, "You do not have permission to view quizzes for this course.")
        return redirect('unauthorized')  # Replace 'unauthorized' with an appropriate URL for unauthorized access

    if request.method == 'POST':
        # Handle form submission
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.created_by = instructor  # Assign the Instructor instance to created_by
            quiz.course = course  # Assign the course instance to the quiz
            quiz.save()
            messages.success(request, "Quiz created successfully!")
            return redirect('quiz_list', course_id=course.id)  # Make sure 'quiz_list' is correct
    else:
        quiz_form = QuizForm()

    return render(request, 'create_quiz.html', {'quiz_form': quiz_form, 'course': course})

# List Quizzes View
# List Quizzes View
@login_required
def quiz_list(request, course_id):
    try:
        # Get the Profile for the logged-in user
        profile = Profile.objects.get(user=request.user)

        # Check if the user is an instructor
        if not profile.isInstructor:
            return HttpResponse("You are not an instructor. Please contact the admin.")
        
        # Get the Instructor instance using the profile's primary key
        instructor = Instructor.objects.get(pk=profile.pk)
    
    except Profile.DoesNotExist:
        return HttpResponse("Profile not found. Please contact the admin.")
    except Instructor.DoesNotExist:
        return HttpResponse("Instructor not found. Please contact the admin.")

    # Ensure the course exists and is owned by the logged-in instructor
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the course is owned by the logged-in instructor
    if course.instructor != instructor:
        # If the course is not owned by the logged-in instructor, redirect to an error page
        messages.error(request, "You do not have permission to view quizzes for this course.")
        return redirect('unauthorized')  # Replace 'unauthorized' with an appropriate URL for unauthorized access

    quizzes = course.quizzes.all()  # Fetch all quizzes related to the course
    return render(request, 'quiz_list.html', {'quizzes': quizzes, 'course': course})

# Add Question View

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    try:
        # Get the Profile for the logged-in user
        profile = Profile.objects.get(user=request.user)

        # Check if the user is an instructor
        if not profile.isInstructor:
            return HttpResponse("You are not an instructor. Please contact the admin.")
        
        # Get the Instructor instance using the profile's primary key
        instructor = Instructor.objects.get(pk=profile.pk)
    except Profile.DoesNotExist:
        return HttpResponse("Profile not found. Please contact the admin.")

    if quiz.created_by != instructor:
        # Ensure the instructor has created this quiz
        messages.error(request, "You do not have permission to add questions to this quiz.")
        return redirect('unauthorized')  # Replace 'unauthorized' with an appropriate URL for unauthorized access

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        choice_forms = [ChoiceForm(request.POST, prefix=f'choice_{i}') for i in range(4)]

        # Validate question and choices
        if question_form.is_valid() and all(c.is_valid() for c in choice_forms):
            # Check for at least one correct choice
            correct_choices = [c.cleaned_data.get('is_correct') for c in choice_forms if c.cleaned_data.get('is_correct')]
            if not correct_choices:
                messages.error(request, "A question must have at least one correct choice.")
            else:
                # Save the question and associated choices
                question = question_form.save(commit=False)
                question.quiz = quiz  # Link the question to the quiz
                question.save()

                for choice_form in choice_forms:
                    choice = choice_form.save(commit=False)
                    choice.question = question  # Link the choice to the question
                    choice.save()

                messages.success(request, "Question added successfully!")
                return redirect('add_question', quiz_id=quiz.id)  # Stay on the same page to add more questions
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        question_form = QuestionForm()
        choice_forms = [ChoiceForm(prefix=f'choice_{i}') for i in range(4)]

    return render(request, 'add_question.html', {
        'quiz': quiz,
        'question_form': question_form,
        'choice_forms': choice_forms,
    })
# Delete Quiz View
@login_required
def delete_quiz(request, quiz_id):
    try:
        # Ensure the logged-in user has a profile
        profile = Profile.objects.get(user=request.user)

        # Check if the user is an instructor
        if not profile.isInstructor:
            return HttpResponse("You are not an instructor. Please contact the admin.")

        # Get the Instructor instance using the profile's primary key
        instructor = Instructor.objects.get(pk=profile.pk)

        # Ensure the quiz exists and is linked to the course owned by the logged-in instructor
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Check if the quiz belongs to a course and ensure the course is owned by the instructor
        if quiz.created_by != instructor:
            messages.error(request, "You do not have permission to delete this quiz.")
            return redirect('quiz_list', course_id=quiz.course.id)

        # Ensure the course is owned by the logged-in instructor
        if quiz.course.instructor != instructor:
            messages.error(request, "You do not have permission to delete a quiz from this course.")
            return redirect('quiz_list', course_id=quiz.course.id)

        # If the quiz is valid and the instructor has permission, delete it
        quiz.delete()
        messages.success(request, "Quiz deleted successfully!")

        # Redirect to the quiz list for the course
        return redirect('quiz_list', course_id=quiz.course.id)
    
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found. Please contact the admin.")
        return redirect('my_courses')  # Redirect to a safe page if profile not found
    except Instructor.DoesNotExist:
        messages.error(request, "Instructor not found. Please contact the admin.")
        return redirect('my_courses')  # Redirect to a safe page if instructor not found
    except Quiz.DoesNotExist:
        messages.error(request, "Quiz not found.")
        return redirect('my_courses')  # Redirect to a safe page if quiz not found
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('my_courses')  # Redirect to a safe page for unexpected errors


def quiz_student_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = Quiz.objects.filter(course=course)  # assuming you have a relation between quizzes and courses
    return render(request, 'quiz_student_list.html', {'course': course, 'quizzes': quizzes})

from student_app.models import Enrollment as StudentEnrollment

@login_required
def take_quiz(request, quiz_id):
    try:
        # Get the profile of the current logged-in user
        profile = Profile.objects.get(user=request.user)

        # Check if the user is a student
        if not profile.isStudent:
            return HttpResponse("You are not a student. Please contact the admin.")

        # Get the User instance using request.user (which is the authenticated user)
        user = request.user

        # Get the Student instance using the related User instance
        student = Student.objects.get(user=user)

        # Get the quiz by ID
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Get all the questions related to the quiz
        questions = quiz.questions.all()

        if request.method == 'POST':
            score = 0
            # Loop through each question and check the answers
            for question in questions:
                selected_choice = request.POST.get(f'question_{question.id}')
                if selected_choice:
                    choice = Choice.objects.get(id=selected_choice)
                    if choice.is_correct:
                        score += 1

            # Create and save the result
            result = Result(
                student=student,
                quiz=quiz,
                score=score,
                percentage=(score / len(questions)) * 100 if questions else 0
            )
            result.calculate_status()  # Calculate the status (Passed/Failed)
            result.save()

            return redirect('quiz_result', quiz_id=quiz.id)  # Redirect to the result page after submission

        return render(request, 'take_quiz.html', {'quiz': quiz, 'questions': questions})

    except Profile.DoesNotExist:
        return HttpResponse("Profile not found. Please contact the admin.")
    except Student.DoesNotExist:
        return HttpResponse("Student not found. Please contact the admin.")
    

@login_required
def quiz_result(request, quiz_id):
    try:
        # Get the profile of the current logged-in user
        profile = Profile.objects.get(user=request.user)

        # Check if the user has a student profile
        if not profile.isStudent:
            return HttpResponse("You are not a student. Please contact the admin.")

        # Get the Student instance associated with the logged-in user
        student = Student.objects.get(user=request.user)

        # Fetch all results for the student and quiz
        results = Result.objects.filter(student=student, quiz__id=quiz_id)

        if not results.exists():
            return HttpResponse("Result not found. Please make sure you have completed the quiz.")

        # Pass all results to the template
        return render(request, 'quiz_result.html', {'results': results})

    except Result.DoesNotExist:
        return HttpResponse("Result not found. Please make sure you have completed the quiz.")
    

@login_required
def manage_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    try:
        # Check if the user is an instructor
        profile = Profile.objects.get(user=request.user)
        if not profile.isInstructor:
            return HttpResponse("You are not an instructor. Please contact the admin.")
        
        # Fetch the instructor instance
        instructor = Instructor.objects.get(pk=profile.pk)
    except Profile.DoesNotExist:
        return HttpResponse("Profile not found. Please contact the admin.")
    
    if quiz.created_by != instructor:
        messages.error(request, "You do not have permission to manage questions for this quiz.")
        return redirect('unauthorized')  # Replace with your unauthorized page or logic

    questions = quiz.questions.all()

    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        messages.success(request, "Question deleted successfully!")
        return redirect('manage_questions', quiz_id=quiz.id)

    return render(request, 'manage_questions.html', {
        'quiz': quiz,
        'questions': questions,
    })