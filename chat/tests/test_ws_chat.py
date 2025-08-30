
import asyncio
import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from elearn.asgi import application
from accounts.factories import UserFactory
from chat.factories import ChatRoomFactory
from chat.models import ChatMessage


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_message_sent_and_received_between_users():
    # Create data safely in async context
    user1 = await sync_to_async(UserFactory.create)()
    user2 = await sync_to_async(UserFactory.create)()
    room = await sync_to_async(ChatRoomFactory.create)()
    await sync_to_async(room.members.add)(user1, user2)

    path = f"/ws/chat/{room.id}/"

    comm1 = WebsocketCommunicator(application, path)
    comm2 = WebsocketCommunicator(application, path)
    try:
        comm1.scope["user"] = user1
        comm2.scope["user"] = user2

        ok1, _ = await comm1.connect()
        ok2, _ = await comm2.connect()
        assert ok1 and ok2

        msg = "Hi there!"
        await comm1.send_json_to({"message": msg})
        resp = await comm2.receive_json_from(timeout=1.0)

        assert resp["message"] == msg
        display_name = await sync_to_async(lambda: user1.profile.public_name)()
        assert resp["display_name"] == display_name

        exists = await sync_to_async(
            ChatMessage.objects.filter(
                room=room, sender=user1, content=msg).exists
        )()
        assert exists
    finally:
        await comm1.disconnect()
        await comm2.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_empty_message_is_ignored():
    user = await sync_to_async(UserFactory.create)()
    room = await sync_to_async(ChatRoomFactory.create)()
    await sync_to_async(room.members.add)(user)

    path = f"/ws/chat/{room.id}/"

    comm = WebsocketCommunicator(application, path)
    try:
        comm.scope["user"] = user
        ok, _ = await comm.connect()
        assert ok

        await comm.send_json_to({"message": "   "})

        # Expect no broadcast back - server may close immediately
        with pytest.raises(asyncio.TimeoutError):
            await comm.receive_json_from(timeout=0.3)

        # Code to avoid teardown errors...
        # Let background tasks run before teardown.
        await asyncio.sleep(0)
    finally:
        try:
            await comm.disconnect()
        except asyncio.CancelledError:
            # App already closed (fine)
            pass
