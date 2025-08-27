from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    name = models.CharField(max_length=128, unique=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chat_rooms",
        blank=True,
    )
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ reference user model safely
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]  # optional: oldest→newest
        indexes = [models.Index(fields=["timestamp"])]  # optional performance

    def __str__(self):
        return f"{self.sender} @ {self.room}: {self.content[:30]}"
