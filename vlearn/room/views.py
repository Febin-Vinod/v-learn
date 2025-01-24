from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Room, Message
from django.db import models

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .models import Room, Message
from authentication_app.models import Profile
from django.utils.text import slugify


@login_required
def rooms(request):
    profile = request.user.profile
    rooms = Room.objects.all()
    return render(request, 'room/rooms.html', {'rooms': rooms})
@login_required
def create_room(request):
    profile = request.user.profile
    
    if not (profile.isInstructor or profile.isAdmin):
        return HttpResponseForbidden("Only instructors and admins can create rooms")
        
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = slugify(name)
        
        room = Room.objects.create(
            name=name,
            slug=slug,
            creator=profile
        )
        room.participants.add(profile)
        return redirect('room', slug=slug)
        
    return render(request, 'room/create_room.html')

@login_required
def room(request, slug):
    profile = request.user.profile
    room = Room.objects.get(slug=slug)
    
    # Check if user has access to this room
    if not (profile.isAdmin or 
            room.creator == profile or 
            room.participants.filter(id=profile.id).exists()):
        return HttpResponseForbidden("You don't have access to this room")
    
    messages = Message.objects.filter(room=room).order_by('date_added')
    return render(request, 'room/room.html', {'room': room, 'messages': messages})