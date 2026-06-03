import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Check if user is authorized for this room
        if await self.is_user_authorized():
            await self.accept()
            
            # Send user join notification
            if self.scope['user'].is_authenticated:
                user_display = self.scope['user'].get_full_name() or self.scope['user'].email
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'system_message',
                        'message': f'{user_display} has joined the chat',
                        'timestamp': timezone.now().isoformat()
                    }
                )
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Send user leave notification
        if self.scope['user'].is_authenticated:
            user_display = self.scope['user'].get_full_name() or self.scope['user'].email
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'system_message',
                    'message': f'{user_display} has left the chat',
                    'timestamp': timezone.now().isoformat()
                }
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Save message to database
        if self.scope['user'].is_authenticated:
            await self.save_message(message)
            
            user = self.scope['user']
            user_display = user.get_full_name() or user.email
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': user.id,
                    'username': user_display,
                    'timestamp': timezone.now().isoformat()
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def system_message(self, event):
        # Send system message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def save_message(self, message):
        room = ChatRoom.objects.get(name=self.room_name)
        ChatMessage.objects.create(
            room=room,
            author=self.scope['user'],
            content=message
        )
        
        # Clean up old messages if this is the global chat
        if room.name == "Global Chat" and not room.is_private:
            messages_count = ChatMessage.objects.filter(room=room).count()
            if messages_count > 1000:
                # Get IDs of oldest messages that exceed the limit
                old_message_ids = ChatMessage.objects.filter(room=room).order_by('timestamp').values_list('id', flat=True)[:messages_count-1000]
                # Delete them
                ChatMessage.objects.filter(id__in=old_message_ids).delete()
    
    @database_sync_to_async
    def is_user_authorized(self):
        # Anonymous users can't access any chat
        if not self.scope['user'].is_authenticated:
            return False
            
        try:
            room = ChatRoom.objects.get(name=self.room_name)
            
            # If room is not private, all authenticated users can access
            if not room.is_private:
                return True
                
            # If room is private, check if user is allowed
            return room.allowed_users.filter(id=self.scope['user'].id).exists()
        except ChatRoom.DoesNotExist:
            return False