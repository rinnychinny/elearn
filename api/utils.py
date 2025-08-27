def is_course_teacher(user, course) -> bool:
    return user == course.creator or course.collaborators.filter(pk=user.pk).exists()
