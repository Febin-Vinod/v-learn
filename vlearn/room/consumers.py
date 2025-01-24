import json
from authentication_app.models import Profile
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Consumer connect called")  # Debug print
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(f"Room name: {self.room_name}")  # Debug print
        self.room_group_name = f'chat_{self.room_name}'
        print(f"Group name: {self.room_group_name}")  # Debug print

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("Accepting connection")  # Debug print
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnecting with code: {close_code}")  # Debug print
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        message = data['message']
        username = data['username']
        room = data['room']

        await self.save_message(username, room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        room = Room.objects.get(slug=room)
        
        Message.objects.create(sender=profile, room=room, content=message)