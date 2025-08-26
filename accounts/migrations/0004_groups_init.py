from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='teacher')
    Group.objects.get_or_create(name='student')

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_alter_userprofile_public_status.py'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]