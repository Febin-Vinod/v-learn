from django.db import models
from authentication_app.models import Instructor

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        Instructor,  # Establish a relationship with the Instructor model
        on_delete=models.CASCADE,
        related_name='courses',
        null= True  # Allows reverse query: instructor.courses.all()
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='courses',
        null=True,
        blank=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    duration = models.CharField(max_length=100, null=True)  
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Video(models.Model):
    title_1 = models.CharField(max_length=200)  # Changed from 'title' to 'title_1'
    video_file = models.FileField(upload_to='course_videos/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_1