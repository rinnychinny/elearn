from django.conf import settings
from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name='courses_teaching', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enrolled_users = models.ManyToManyField(User, blank=True, related_name='courses_enrolled')

    def save(self, *args, **kwargs):
        # automatically add creator as a collaborator when saving on newly created
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.collaborators.add(self.creator)

    def __str__(self):
        return self.title
