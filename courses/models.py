from django.db import models
from django.db.models import Avg, Count

from django.contrib.auth import get_user_model
User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        User, related_name='courses_created', on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(
        User, related_name='courses_teaching', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    enrolled_users = models.ManyToManyField(
        User,
        through='Enrollment',
        related_name='courses_enrolled',
        blank=True,
    )

    def save(self, *args, **kwargs):
        # automatically add creator as a collaborator when saving on newly created
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.collaborators.add(self.creator)

    def __str__(self):
        return self.title

    def average_rating(self):
        return self.feedbacks.aggregate(avg=Avg("rating"))["avg"]

    def feedback_count(self):
        return self.feedbacks.aggregate(c=Count("id"))["c"]


class Material(models.Model):

    course = models.ForeignKey(
        Course, related_name='materials', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    content = models.FileField(
        upload_to='course_materials/', blank=True, null=True)

    def __str__(self):
        return self.title


class CourseFeedback(models.Model):

    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="course_feedbacks")
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(0, 11)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # one feedback per course per user
        unique_together = ('course', 'user')
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} feedback for {self.course}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    blocked = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
