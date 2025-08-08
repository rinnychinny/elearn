from django import forms
from .models import UserProfile

# form for viewing/updating user profile information
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['public_name', 'public_status', 'public_bio']
