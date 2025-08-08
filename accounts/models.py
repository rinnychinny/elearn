from django.db import models
from django.contrib.auth.models import User

# Extend default user model with additional custom fields
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    public_name = models.TextField(unique=True, null=False, blank=False)
    public_status = models.TextField(unique=False, null=False, blank=True,  default = '')
    public_bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'
