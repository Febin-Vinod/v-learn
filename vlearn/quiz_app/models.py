from django.db import models
from django.contrib.auth.models import User
from authentication_app.models import Instructor
from instructor.models import Course  # Assuming the Course model is in the instructor_app

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="quizzes"
    )  # A quiz is associated with a course
    created_by = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="quizzes"
    )  # Instructor who created the quiz
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.title}"  # Include course name for clarity

class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions"
    )  # A question belongs to a quiz
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"Question: {self.text} (Quiz: {self.quiz.title})"

class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )  # A choice belongs to a question
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class Result(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="results"
    )  # A result belongs to a student
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="results"
    )  # A result is for a specific quiz
    score = models.IntegerField()
    taken_at = models.DateTimeField(auto_now_add=True)
    percentage = models.FloatField(null=True, blank=True)  # Store the score percentage
    status = models.CharField(
        max_length=10,
        choices=[("Passed", "Passed"), ("Failed", "Failed")],
        default="Failed",
        null=True,
    )  # Pass or fail status
    previous_attempts = models.BooleanField(default=False)  # Track if passed earlier

    def __str__(self):
        return (
            f"{self.user.username} - {self.quiz.title}: {self.score}/{self.quiz.questions.count()}"
        )

    def calculate_status(self):
        """
        Calculates the percentage and determines if the user has passed the quiz.
        """
        total_questions = self.quiz.questions.count()
        self.percentage = (self.score / total_questions) * 100 if total_questions > 0 else 0
        self.status = "Passed" if self.percentage >= 75 else "Failed"
        self.previous_attempts = (
            self.quiz.results.filter(user=self.user, status="Passed").exists()
        )  # Check if passed in prior attempts
        self.save()
