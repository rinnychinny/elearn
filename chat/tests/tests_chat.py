import asyncio
import pytest
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from django.urls import reverse
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from elearn.asgi import application
from ..factories import ChatRoomFactory
from ..models import ChatMessage
from accounts.factories import UserFactory


@pytest.mark.asyncio
async def test_message_sent_and_received_between_users():
    user1 = UserFactory()
    user2 = UserFactory()
    room = ChatRoomFactory()
    room.members.add(user1, user2)

    communicator1 = WebsocketCommunicator(
        application, f"/ws/chat/{room.name}/")
    communicator1.scope['user'] = user1
    connected1, _ = await communicator1.connect()
    assert connected1

    communicator2 = WebsocketCommunicator(
        application, f"/ws/chat/{room.name}/")
    communicator2.scope['user'] = user2
    connected2, _ = await communicator2.connect()
    assert connected2

    test_message = "Hi there!"
    await communicator1.send_json_to({"message": test_message})

    response = await communicator2.receive_json_from()
    assert response['message'] == test_message
    assert response['display_name'] == user1.profile.public_name

    # Check message saved in DB
    exists = await database_sync_to_async(
        ChatMessage.objects.filter(
            room=room, sender=user1, content=test_message).exists
    )()
    assert exists

    await communicator1.disconnect()
    await communicator2.disconnect()


@pytest.mark.asyncio
async def test_empty_message_is_ignored():
    user = UserFactory()
    room = ChatRoomFactory()
    room.members.add(user)

    communicator = WebsocketCommunicator(application, f"/ws/chat/{room.name}/")
    communicator.scope['user'] = user
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({"message": "   "})

    # Wait for a short time and ensure no message was sent back
    try:
        msg = await communicator.receive_json_from(timeout=1)
        # If message received, fail
        assert False, "Received an unexpected message for empty input"
    except asyncio.TimeoutError:
        # Expected: no message received
        pass

    await communicator.disconnect()


class ChatFunctionalTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        # Assert profiles exist for the users
        self.assertTrue(hasattr(self.user1, 'profile'))
        self.assertIsNotNone(getattr(self.user1.profile, 'public_name', None))
        self.assertTrue(hasattr(self.user2, 'profile'))
        self.assertIsNotNone(getattr(self.user2.profile, 'public_name', None))

        self.room = ChatRoomFactory()
        self.room.members.add(self.user1, self.user2)

    def connect_user(self, user):
        communicator = WebsocketCommunicator(
            application, f"/ws/chat/{self.room.name}/")
        communicator.scope['user'] = user
        connected, _ = async_to_sync(communicator.connect)()
        self.assertTrue(connected)
        return communicator

    def test_message_sent_and_received_between_users(self):

        communicator1 = self.connect_user(self.user1)

        communicator2 = self.connect_user(self.user2)

        test_message = "Hi there!"
        async_to_sync(communicator1.send_json_to)({"message": test_message})

        # User2 receives message
        response = async_to_sync(communicator2.receive_json_from)()

        self.assertEqual(response['message'], test_message)
        self.assertEqual(response['display_name'],
                         self.user1.profile.public_name)

        # Confirm message saved in DB
        queryset = ChatMessage.objects.filter(
            room=self.room, sender=self.user1, content=test_message)
        self.assertTrue(queryset.exists())

        async_to_sync(communicator1.disconnect)()
        async_to_sync(communicator2.disconnect)()

    def test_unauthenticated_user_cannot_connect(self):
        from django.contrib.auth.models import AnonymousUser
        communicator = WebsocketCommunicator(
            application, f"/ws/chat/{self.room.name}/")
        communicator.scope['user'] = AnonymousUser()
        connected, _ = async_to_sync(communicator.connect)()
        self.assertFalse(connected)

    def test_empty_message_is_ignored(self):
        communicator = self.connect_user(self.user1)
        async_to_sync(communicator.send_json_to)({"message": "   "})

        # No broadcast should be sent to the sender
        with self.assertRaises(async_to_sync(communicator.receive_json_from)().__class__.Exception):
            async_to_sync(communicator.receive_json_from)()

        async_to_sync(communicator.disconnect)()

    def test_user_subscription_post(self):

        self.client.force_login(self.user1)

        url = reverse('chat:chat_room', kwargs={'room_name': self.room.name})

        # Unsubscribe test
        response = self.client.post(
            url, {'action': 'unsubscribe'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user1, self.room.members.all())

        # Subscribe test
        response = self.client.post(
            url, {'action': 'subscribe'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user1, self.room.members.all())
