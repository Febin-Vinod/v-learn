from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Instructor, Student, Admin

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Common serializer for profile data
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        fields = ['user', 'full_name', 'phone', 'address']

class InstructorSerializer(ProfileSerializer):
    class Meta:
        model = Instructor
        fields = ProfileSerializer.Meta.fields + ['qualification', 'bio']

class StudentSerializer(ProfileSerializer):
    class Meta:
        model = Student
        fields = ProfileSerializer.Meta.fields + ['school']

class AdminSerializer(ProfileSerializer):
    class Meta:
        model = Admin
        fields = ProfileSerializer.Meta.fields + ['department']
