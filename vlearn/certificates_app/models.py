from django.db import models
from django.contrib.auth.models import User
from instructor.models import Course
from student_app.models import Enrollment
import uuid

class Certificate(models.Model):
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Certificate-{self.certificate_id}-{self.student.username}-{self.course.title}"