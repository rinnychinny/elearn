from celery import shared_task
from django.contrib.auth.models import User
from .models import Course
from accounts.models import Notification


@shared_task
def notify_teacher_of_enrollment(teacher_id, student_name, course_title):
    teacher = User.objects.get(id=teacher_id)
    message = f"{student_name} has enrolled in your course: {course_title}."
    print(f"Notification to {teacher_id}: {message}")
    Notification.objects.create(
        user=teacher_id,
        message=f"{student_name} has enrolled in your course {course_title}."
    )
