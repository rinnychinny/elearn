import factory
from accounts.factories import UserFactory
from chat.models import ChatRoom, ChatMessage


class ChatRoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatRoom

    name = factory.Sequence(lambda n: f'room{n}')


class ChatMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatMessage

    room = factory.SubFactory(ChatRoomFactory)
    sender = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence')
