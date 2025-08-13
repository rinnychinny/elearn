from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import Course
from .forms import CourseForm

# Mixin to limit access to users in 'teacher' group
class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='teacher').exists()

class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('courses:course_list')  # Redirect after success

    def form_valid(self, form):
        form.instance.creator = self.request.user  # set creator
        return super().form_valid(form)


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

