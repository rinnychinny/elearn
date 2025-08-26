from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User


class Command(BaseCommand):
    help = 'Create initial groups and users for elearn app'

    def handle(self, *args, **kwargs):
        # Create groups
        teacher_group, _ = Group.objects.get_or_create(name='teacher')
        student_group, _ = Group.objects.get_or_create(name='student')

        # Create admin superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 'admin@elearn.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Created admin superuser'))

        # Create teacher user
        if not User.objects.filter(username='teacher1').exists():
            teacher_user = User.objects.create_user(
                'teacher1', password='elearn123')
            teacher_user.groups.add(teacher_group)
            teacher_user.save()
            self.stdout.write(self.style.SUCCESS('Created teacher user'))

        # Create student user
        if not User.objects.filter(username='student1').exists():
            student_user = User.objects.create_user(
                'student1', password='elearn123')
            student_user.groups.add(student_group)
            student_user.save()
            self.stdout.write(self.style.SUCCESS('Created student user'))
