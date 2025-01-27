from django.contrib import admin
from .models import Instructor, Student, Admin, Profile
admin.site.register(Profile)
admin.site.register(Instructor)
admin.site.register(Student)
admin.site.register(Admin)
