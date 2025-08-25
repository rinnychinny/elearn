import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage, ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_display_name(self, user):
        return user.profile.public_name

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        user = self.scope['user']
        if not user.is_authenticated:
            # Reject the connection if not authenticated
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        user = self.scope['user']
        if not user.is_authenticated:
            # Ignore messages from unauthenticated users
            return

        data = json.loads(text_data)
        message = data.get('message', '').strip()
        if not message:
            return

        chat_message = await self.save_message(user, self.room_name, message)

        display_name = await self.get_display_name(user)

        # Broadcast message to room group including user's display name from profile
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # specifies handler method
                'message': message,
                'display_name': display_name,
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket client
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'display_name': event['display_name'],
        }))

    @database_sync_to_async
    def save_message(self, user, room_name, message):
        room = ChatRoom.objects.get(name=room_name)
        return ChatMessage.objects.create(sender=user, room=room, content=message)
