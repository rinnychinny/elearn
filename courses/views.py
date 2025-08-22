
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from django.views import View
from django.views.generic import CreateView, ListView, DetailView

from django.views.generic.edit import DeleteView
from .models import Course, Material, CourseFeedback
from .forms import CourseForm, MaterialForm, CourseFeedbackForm

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
        # Return an empty queryset as detailed lists sent via context.
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

        return context


class CourseDetailView(LoginRequiredMixin, DetailView):

    model = Course
    template_name = 'courses/course_detail_base.html'
    context_object_name = 'course'

    SECTION_TEMPLATES = {
        "materials":    "courses/course_detail_materials.html",
        "feedback":     "courses/course_detail_feedback.html",
        "teacher_area": "courses/course_detail_teacher_area.html",
        "registration": "courses/coure_detail_registration.html",
    }
    DEFAULT_SECTION = "materials"

    def get_section(self):
        # /courses/<pk>/<section>/ or fallback to ?section=… or default
        return (
            self.kwargs.get("section")
            or self.request.GET.get("section")
            or self.DEFAULT_SECTION
        )

    def get_template_names(self):
        section = self.get_section()
        tpl = self.SECTION_TEMPLATES.get(section)
        if not tpl:
            raise Http404("Unknown section")
        return [tpl]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user

        context["active_section"] = self.DEFAULT_SECTION

        # helper flags for template logic
        context['is_enrolled'] = course.enrolled_users.filter(
            id=user.id).exists()

        # course detail
        context['course_title'] = course.title
        context['course_description'] = course.description
        context['course_creator'] = course.creator
        context['course_collaborators'] = course.collaborators.all()
        context['materials'] = course.materials.order_by('order')
        context['students'] = course.enrolled_users.all()

        # course review data
        feedback = course.feedbacks.select_related(
            'user').order_by('-created_at')
        context['feedbacks'] = feedback

        if user.is_authenticated:
            is_student = user.groups.filter(name='student').exists()
            context['is_student'] = is_student
            already = feedback.filter(user=user).exists()
            context['already_reviewed'] = already
            context['can_review'] = is_student and context['is_enrolled'] and not already
            # provide a crispy form only when they can review
            if context['can_review']:
                context['feedback_form'] = CourseFeedbackForm(
                    user=user, course=course)

        return context


class MaterialCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'courses/material_form.html'

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.kwargs['course_id']})

    def form_valid(self, form):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        form.instance.course = course
        return super().form_valid(form)


class MaterialDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):

    model = Material
    template_name = 'courses/material_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.object.course.id})


class MaterialMoveView(View):
    def get(self, request, material_id, direction):
        material = get_object_or_404(Material, id=material_id)

        if direction == 'up':
            previous = Material.objects.filter(
                course=material.course, order__lt=material.order).order_by('-order').first()
            if previous:
                material.order, previous.order = previous.order, material.order
                material.save()
                previous.save()
        elif direction == 'down':
            next = Material.objects.filter(
                course=material.course, order__gt=material.order).order_by('order').first()
            if next:
                material.order, next.order = next.order, material.order
                material.save()
                next.save()

        return redirect('courses:course_detail', pk=material.course.id)


class EnrollView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        course.enrolled_users.add(request.user)
        return redirect('courses:course_detail', pk=course_id)


class DisenrollView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        course.enrolled_users.remove(request.user)
        return redirect('courses:course_detail', pk=course_id)


class FeedbackCreateView(LoginRequiredMixin, View):
    """
    POST-only endpoint from:
      <form method="post" action="{% url 'courses:course_feedback_create' course.id %}">
    """

    def post(self, request, pk, *args, **kwargs):
        course = get_object_or_404(Course, pk=pk)

        # must be enrolled
        if not course.enrolled_users.filter(pk=request.user.pk).exists():
            messages.error(request, "You must be enrolled to leave feedback.")
            return redirect("courses:course_detail", pk=course.pk)

        # only one feedback per user per course
        if CourseFeedback.objects.filter(course=course, user=request.user).exists():
            messages.info(request, "You’ve already reviewed this course.")
            return redirect("courses:course_detail", pk=course.pk)

        # Bind and then validate the form
        form = CourseFeedbackForm(
            request.POST, user=request.user, course=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for your feedback!")
            return redirect("courses:course_detail", pk=course.pk)

        # If invalid, show a generic message and bounce back
        messages.error(
            request, "Please correct the errors in your feedback form.")
        return redirect("courses:course_detail", pk=course.pk)
