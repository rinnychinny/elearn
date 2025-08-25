from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from asgiref.sync import async_to_sync
from elearn.asgi import application
from chat.factories import ChatRoomFactory
from chat.models import ChatMessage
from accounts.factories import UserFactory


class ChatFunctionalTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
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
        from django.test import Client
        client = Client()
        client.force_login(self.user1)

        # Unsubscribe test
        response = client.post(
            f'/chat/{self.room.name}/', {'action': 'unsubscribe'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user1, self.room.members.all())

        # Subscribe test
        response = client.post(
            f'/chat/{self.room.name}/', {'action': 'subscribe'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user1, self.room.members.all())
