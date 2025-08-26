from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User, Permission


class Command(BaseCommand):
    help = 'Create initial groups and users for elearn app'

    def handle(self, *args, **kwargs):
        # Create groups or get existing ones
        admin_group, _ = Group.objects.get_or_create(name='admin')
        teacher_group, _ = Group.objects.get_or_create(name='teacher')
        student_group, _ = Group.objects.get_or_create(name='student')

        # Assign all permissions to admin_group
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)
        admin_group.save()
        self.stdout.write(self.style.SUCCESS(
            'Assigned all permissions to admin group'))

        # Admin user
        admin_user, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@elearn.com',
            'is_superuser': True,
            'is_staff': True,
        })
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin superuser'))
        else:
            self.stdout.write('Admin user already exists')

        # Always assign admin group
        admin_user.groups.add(admin_group)
        admin_user.save()

        # Teacher user
        teacher_user, created = User.objects.get_or_create(username='teacher1')
        if created:
            teacher_user.set_password('elearn123')
            teacher_user.save()
            self.stdout.write(self.style.SUCCESS('Created teacher user'))
        else:
            self.stdout.write('Teacher user already exists')

        teacher_user.groups.add(teacher_group)
        teacher_user.save()

        # Student user
        student_user, created = User.objects.get_or_create(username='student1')
        if created:
            student_user.set_password('elearn123')
            student_user.save()
            self.stdout.write(self.style.SUCCESS('Created student user'))
        else:
            self.stdout.write('Student user already exists')

        student_user.groups.add(student_group)
        student_user.save()
