from django.contrib.auth.models import User
from django.db import models

# Shared base for profiles
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
   
    # Role Flags
    isAdmin = models.BooleanField(default=False)
    isStudent = models.BooleanField(default=False)
    isInstructor = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile: {self.full_name}"

# Concrete models inheriting from Profile   
class Instructor(Profile):
    qualification = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Set isInstructor flag to True
        self.isInstructor = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

class Student(Profile):
    school = models.CharField(max_length=20)
    

    def save(self, *args, **kwargs):
        # Set isStudent flag to True
        self.isStudent = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Student: {self.full_name}, School: {self.school}"

class Admin(Profile):
    department = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Set isAdmin flag to True
        self.isAdmin = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Admin: {self.full_name}"
