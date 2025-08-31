from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import UserProfile

# form for viewing/updating user profile information


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['public_name', 'public_status', 'public_bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'  # Use POST method for form
        # Add submit button
        self.helper.add_input(Submit('submit', 'Save Profile'))
