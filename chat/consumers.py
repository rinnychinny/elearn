import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage, ChatRoom
import json
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_display_name(self, user):
        return user.profile.public_name

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

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
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def receive(self, text_data):
        # new chat message has been sent to the socket
        try:
            # Get user from scope and verify authenticated
            user = self.scope.get('user', None)
            if not user or not user.is_authenticated:
                logger.info("Unauthenticated user, ignoring message")
                return

            # Parse JSON data and extract message
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            if not message:
                logger.info("Ignoring empty message")
                return

            # Save message in DB using room_id (set on connect)
            await self.save_message(user, self.room_id, message)

            # Get display name from user profile
            display_name = await self.get_display_name(user)

            # Broadcast message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',      # Calls chat_message method
                    'message': message,
                    'display_name': display_name,
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {e}", exc_info=True)

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'display_name': event['display_name'],
            }))
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)

    @database_sync_to_async
    def save_message(self, user, room_id, message):
        room = ChatRoom.objects.get(id=room_id)
        return ChatMessage.objects.create(sender=user, room=room, content=message)
