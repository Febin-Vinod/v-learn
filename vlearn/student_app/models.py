from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price field with decimal precision
    duration = models.CharField(max_length=100, null=True)  # Duration field, you can adjust max length as needed

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
