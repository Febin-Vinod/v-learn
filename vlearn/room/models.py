from django.contrib.auth.models import User
from django.db import models

from django.db import models
from authentication_app.models import Profile

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    # Add creator field to track who created the room
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='created_rooms')
    # Add participants to manage who can join
    participants = models.ManyToManyField(Profile, related_name='joined_rooms')
    
    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)