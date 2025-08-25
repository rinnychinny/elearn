from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()


class ChatRoom(models.Model):
    name = models.CharField(max_length=128, unique=True)
    members = models.ManyToManyField(
        User, related_name='chat_rooms', blank=True)
    description = models.CharField(max_length=256)


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)
