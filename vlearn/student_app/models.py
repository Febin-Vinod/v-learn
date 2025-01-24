from django.db import models
from instructor.models import Course
# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
