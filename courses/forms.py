from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from crispy_forms.layout import Layout, Field, HTML

from .models import Course, Material, CourseFeedback

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create Course'))

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'content', 'order'] 


class CourseFeedbackForm(forms.ModelForm):
    class Meta:
        model = CourseFeedback
        fields = ["rating", "comment"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.course = kwargs.pop("course")
        super().__init__(*args, **kwargs)

        # Crispy setup
        self.helper = FormHelper()
        self.helper.form_tag = False #template has the <form> tag
        self.helper.layout = Layout(
            HTML("{% if form.non_field_errors %}<div class='text-danger mb-2'>{{ form.non_field_errors }}</div>{% endif %}"),
            Field("rating"),
            Field("comment"),
        )

    def clean(self):
        cleaned = super().clean()
        # Ensure user is enrolled before allowing feedback
        if not self.course.enrolled_users.filter(pk=self.user.pk).exists():
            raise forms.ValidationError("You must be enrolled in this course to leave feedback.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.user = self.user
        obj.course = self.course
        if commit:
            obj.save()
        return obj
