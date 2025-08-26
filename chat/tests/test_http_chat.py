import pytest
from django.urls import reverse
from accounts.factories import UserFactory
from chat.factories import ChatRoomFactory


@pytest.mark.django_db
def test_user_subscription_post(client):
    user = UserFactory()
    room = ChatRoomFactory()
    client.force_login(user)

    url = reverse("chat:chat_room", kwargs={"room_id": room.id})

    resp = client.post(url, {"action": "unsubscribe"})
    assert resp.status_code == 302
    assert user not in room.members.all()

    resp = client.post(url, {"action": "subscribe"})
    assert resp.status_code == 302
    assert user in room.members.all()
