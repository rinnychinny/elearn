from celery import shared_task
from .models import Course
from accounts.models import Notification


@shared_task
def notify_teacher_of_enrollment(teacher_id, student_name, course_title):
    message = f"{student_name} has enrolled in your course: {course_title}."
    print(f"Notification to {teacher_id}: {message}")
    Notification.objects.create(
        user_id=teacher_id,
        message=f"{student_name} has enrolled in your course {course_title}."
    )


@shared_task
def notify_students_new_material(course_id, material_title):
    course = Course.objects.get(id=course_id)
    enrolled_students = course.enrolled_users.all()
    message = f"New material '{material_title}' has been added to your course '{course.title}'."
    notifications = [
        Notification(user=student, message=message)
        for student in enrolled_students
    ]
    Notification.objects.bulk_create(notifications)
