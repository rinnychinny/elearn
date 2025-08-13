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

    def get_queryset(self):
        # Return an empty queryset or a generic one (optional),
        # since you'll send the detailed lists via context anyway.
        return Course.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # All courses available (could be filtered as needed)
        context['all_courses'] = Course.objects.all()

        # Courses the user created
        context['created_courses'] = Course.objects.filter(creator=user)

        # Courses where the user is a collaborator (but not creator)
        context['collaborating_courses'] = Course.objects.filter(
            collaborators=user
        ).exclude(creator=user)

        # Courses the user is enrolled in
        context['enrolled_courses'] = user.courses_enrolled.all()

        # define some helper flags for the roles
        context['is_teacher'] = user.groups.filter(name='teacher').exists()
        context['is_student'] = user.groups.filter(name='student').exists()

        return context
